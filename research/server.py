"""Loopback-only HTTP status controller for non-destructive research artifacts."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from simulator import ResearchWorkspace


def serve(workspace: ResearchWorkspace, port: int = 8765):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if urlsplit(self.path).path != "/status":
                self.send_error(404)
                return
            body = json.dumps(workspace.status()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    # No remote binding, execution endpoint, agent registration, or remote commands.
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Local status: http://127.0.0.1:{server.server_port}/status")
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path("./research-workspace"))
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(ResearchWorkspace(args.workspace), args.port)
