"""Static server for the render page that also accepts POST /frame?i=N (PNG body) and writes frames/NNNN.png."""
import http.server
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames")


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        data = self.rfile.read(int(self.headers["Content-Length"]))
        os.makedirs(FRAMES, exist_ok=True)
        if self.path.startswith("/frame"):
            with open(os.path.join(FRAMES, f"{int(q['i'][0]):04d}.png"), "wb") as f:
                f.write(data)
        elif self.path.startswith("/done"):
            open(os.path.join(FRAMES, "DONE"), "w").write(data.decode())
        self.send_response(204); self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 4195), H).serve_forever()
