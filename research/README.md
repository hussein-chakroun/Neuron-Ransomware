# Neuron safe research workspace

This is a separate, **non-destructive** research simulator. It does **not** run the historical ransomware agent, encrypt files, delete originals, deploy payloads, or expose a command-and-control endpoint.

Requirements: Python 3.9+; standard library only.

From the repository root:

```sh
python research/cli.py status
```

Place disposable sample files in `research-workspace/inputs/`, then:

```sh
python research/cli.py simulate sample.txt
python research/cli.py restore sample.txt.sim
python research/server.py --port 8765
```

The HTTP controller exposes **read-only** `http://127.0.0.1:8765/status` and binds only to localhost. Simulation uses reversible compressed artifacts, **not encryption**. Restores are compared with preserved originals using SHA-256 and written exclusively into `restored/`. Original inputs and artifacts are never deleted or overwritten. The simulator refuses inputs larger than 32 MiB.

Run tests with `python -m unittest discover -s research -p 'test_*.py'`.

**Important:** The historical code under `Neuron Ransomeware/` is potentially destructive and has not been made safe by these additions. Do not execute it. No end-to-end malware deployment or remote control functionality is provided.
