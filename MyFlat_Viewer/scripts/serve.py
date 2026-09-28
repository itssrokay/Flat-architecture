"""Local web server for the MyFlat Viewer that never lets the browser use stale copies.
Usage (from the MyFlat_Viewer folder):
    python3 scripts/serve.py [port]          this computer only   -> http://localhost:8080/
    python3 scripts/serve.py [port] --lan    also phones/tablets on the same Wi-Fi -> http://<this computer's IP>:8080/"""
import http.server, os, socket, sys

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()
    def log_message(self, *a):
        pass

def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("10.255.255.255", 1)); ip = s.getsockname()[0]; s.close(); return ip
    except Exception:
        return None

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lan = "--lan" in sys.argv
    port = int(args[0]) if args else 8080
    print(f"MyFlat Viewer: http://localhost:{port}/")
    if lan and lan_ip(): print(f"On your phone (same Wi-Fi): http://{lan_ip()}:{port}/")
    sys.stdout.flush()
    http.server.ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", port), NoCache).serve_forever()
