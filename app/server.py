"""Minimal HTTP service for the StreamForge DevOps portfolio project.

Uses only the Python standard library. Endpoints:
    GET /        -> simple HTML page
    GET /health  -> JSON health check, HTTP 200
Any other path returns 404.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
VERSION = os.environ.get("APP_VERSION", "0.1.0")

HOME_PAGE = (
    "<!doctype html>\n"
    "<html lang=\"en\">\n"
    "<head><meta charset=\"utf-8\"><title>StreamForge</title></head>\n"
    "<body>\n"
    "<h1>StreamForge</h1>\n"
    "<p>Demo HTTP service for a DevOps / Kubernetes portfolio project.</p>\n"
    f"<p>Version: {VERSION}</p>\n"
    "</body>\n"
    "</html>\n"
)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(200, HOME_PAGE, "text/html; charset=utf-8")
        elif path == "/health":
            body = json.dumps({"status": "ok"})
            self._send(200, body, "application/json")
        else:
            body = json.dumps({"error": "not found"})
            self._send(404, body, "application/json")


def create_server(host=HOST, port=PORT):
    """Create (but do not start) the HTTP server. Port 0 picks a free port."""
    return ThreadingHTTPServer((host, port), Handler)


def main():
    server = create_server()
    print(f"Listening on {HOST}:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()