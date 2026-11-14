"""Non-destructive, local-only file recovery simulator.

This intentionally does NOT encrypt, delete, or overwrite source files.
It creates reversible, integrity-checked test artifacts inside a workspace.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import zlib

MAGIC = b"NEURON-SIM-1\n"
MAX_INPUT_BYTES = 32 * 1024 * 1024


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


class ResearchWorkspace:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.inputs = self.root / "inputs"
        self.artifacts = self.root / "artifacts"
        self.restored = self.root / "restored"
        for folder in (self.inputs, self.artifacts, self.restored):
            folder.mkdir(parents=True, exist_ok=True)

    def _input(self, name: str) -> Path:
        if not name or Path(name).name != name or name in (".", ".."):
            raise ValueError("Use a single input filename")
        path = self.inputs / name
        if path.is_symlink() or not path.is_file() or not _inside(path.resolve(), self.inputs.resolve()):
            raise ValueError("Input must be a regular file in workspace/inputs")
        return path

    @staticmethod
    def _write_new(path: Path, data: bytes) -> None:
        # Exclusive creation prevents overwriting existing files or symlinks.
        with path.open("xb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())

    def simulate(self, name: str) -> dict:
        source = self._input(name)
        if source.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("Input exceeds 32 MiB simulator limit")
        data = source.read_bytes()
        if len(data) > MAX_INPUT_BYTES:
            raise ValueError("Input changed during read")
        digest = hashlib.sha256(data).hexdigest()
        # Reversible packaging only: deliberately not cryptographic encryption.
        payload = MAGIC + zlib.compress(data)
        artifact = self.artifacts / (name + ".sim")
        self._write_new(artifact, payload)
        return {"name": name, "sha256": digest, "artifact": artifact.name,
                "source_preserved": source.exists(), "bytes": len(data)}

    def restore(self, name: str) -> dict:
        if not name or Path(name).name != name or not name.endswith(".sim"):
            raise ValueError("Expected a single .sim artifact filename")
        artifact = self.artifacts / name
        if artifact.is_symlink() or not artifact.is_file():
            raise ValueError("Artifact not found")
        if artifact.stat().st_size > MAX_INPUT_BYTES + 1024 * 1024:
            raise ValueError("Artifact too large")
        payload = artifact.read_bytes()
        if not payload.startswith(MAGIC):
            raise ValueError("Invalid simulator artifact")
        decoder = zlib.decompressobj()
        data = decoder.decompress(payload[len(MAGIC):], MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES or not decoder.eof or decoder.unused_data:
            raise ValueError("Invalid or oversized artifact")
        data += decoder.flush()
        if len(data) > MAX_INPUT_BYTES:
            raise ValueError("Restored data too large")
        original_name = name[:-4]
        source = self._input(original_name)
        digest = hashlib.sha256(data).hexdigest()
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError("Restored content does not match preserved original")
        output = self.restored / original_name
        self._write_new(output, data)
        return {"name": original_name, "sha256": digest, "verified": True,
                "original_preserved": source.exists(), "artifact_preserved": artifact.exists()}

    def status(self) -> dict:
        return {"workspace": str(self.root),
                "inputs": sorted(p.name for p in self.inputs.iterdir() if p.is_file() and not p.is_symlink()),
                "artifacts": sorted(p.name for p in self.artifacts.iterdir() if p.is_file() and not p.is_symlink()),
                "restored": sorted(p.name for p in self.restored.iterdir() if p.is_file() and not p.is_symlink())}
