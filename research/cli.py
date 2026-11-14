"""Local CLI for safe simulator operations."""
import argparse
import json
from pathlib import Path
from simulator import ResearchWorkspace

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["status", "simulate", "restore"])
    parser.add_argument("filename", nargs="?")
    parser.add_argument("--workspace", type=Path, default=Path("./research-workspace"))
    args = parser.parse_args()
    workspace = ResearchWorkspace(args.workspace)
    if args.command == "status":
        result = workspace.status()
    elif not args.filename:
        parser.error("filename is required for simulate and restore")
    elif args.command == "simulate":
        result = workspace.simulate(args.filename)
    else:
        result = workspace.restore(args.filename)
    print(json.dumps(result, indent=2))
