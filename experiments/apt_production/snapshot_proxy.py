#!/usr/bin/env python3
import http.server, socketserver, urllib.request, urllib.error, pathlib, sys

PORT = int(sys.argv[1])
TARGET = pathlib.Path(sys.argv[2])

class Proxy(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def do_GET(self): self._proxy(False)
    def do_HEAD(self): self._proxy(True)
    def log_message(self, fmt, *args):
        sys.stderr.write("proxy " + (fmt % args) + "\n")
    def _proxy(self, head):
        stamp = TARGET.read_text().strip()
        if not self.path.startswith("/debian/"):
            self.send_error(404)
            return
        rel = self.path[len("/debian/"):]
        url = f"https://snapshot.debian.org/archive/debian/{stamp}/{rel}"
        req = urllib.request.Request(url, method="HEAD" if head else "GET",
                                     headers={"User-Agent":"EEQ-production-replay/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = b"" if head else r.read()
                self.send_response(r.status)
                for k,v in r.headers.items():
                    lk=k.lower()
                    if lk in {"content-type","content-length","last-modified","etag","content-encoding"}:
                        if lk=="content-length" and not head:
                            v=str(len(body))
                        self.send_header(k,v)
                self.send_header("X-EEQ-Upstream", url)
                self.end_headers()
                if not head: self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_error(e.code, f"upstream {url}: {e.reason}")
        except Exception as e:
            self.send_error(502, f"upstream {url}: {e}")

with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Proxy) as httpd:
    httpd.serve_forever()
