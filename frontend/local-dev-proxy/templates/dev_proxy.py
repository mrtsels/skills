#!/usr/bin/env python3
"""
Dev proxy: serves static frontend on :PORT, proxies /api/ to BACKEND.
Copy this to your project root and adjust BACKEND/port as needed.
"""
import http.server
import urllib.request
import urllib.error
import os

BACKEND = "http://localhost:8080"
PORT = 3000
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(405)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(405)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(405)

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(405)

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods",
                             "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()
            return
        self.send_error(405)

    def _proxy(self):
        body = None
        length = int(self.headers.get("Content-Length", 0))
        if length > 0:
            body = self.rfile.read(length)

        url = BACKEND + self.path
        req = urllib.request.Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length", "transfer-encoding"):
                req.add_header(k, v)

        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "content-encoding", "content-length"):
                        self.send_header(k, v)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding", "content-encoding", "content-length"):
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def translate_path(self, path):
        path = super().translate_path(path)
        if os.path.isdir(path):
            for index in ("index.html", "index.htm"):
                idx = os.path.join(path, index)
                if os.path.exists(idx):
                    return idx
        return path


if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
    print(f"Dev proxy on http://localhost:{PORT} (static served locally, /api/ → {BACKEND})")
    server.serve_forever()
