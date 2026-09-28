"""Local web server for the MyFlat Viewer that never lets the browser use stale copies.
Usage (from the MyFlat_Viewer folder):
    python3 scripts/serve.py [port]          this computer only   -> http://localhost:8080/
    python3 scripts/serve.py [port] --lan    also phones/tablets on the same Wi-Fi -> http://<this computer's IP>:8080/
The 💬 Ask chat works locally too: put OPENAI_API_KEY=sk-... in a file named .env in the MyFlat_Viewer folder
(it is git-ignored) or set it in the environment. Same rules as the Vercel function in api/chat.js."""
import http.server, os, socket, sys, json, re, urllib.request, urllib.error

def env(name, default=None):
    if os.environ.get(name): return os.environ[name]
    try:
        for line in open(".env", encoding="utf-8"):
            k, _, v = line.strip().partition("=")
            if k.strip() == name: return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return default

def chat(body):
    """same prompt as api/chat.js (the rules text is read from that file so there is one copy)"""
    key = env("OPENAI_API_KEY")
    if not key: return 500, {"error": "No OPENAI_API_KEY: add it to a .env file in the MyFlat_Viewer folder (OPENAI_API_KEY=sk-...) and restart the server."}
    src = open("api/chat.js", encoding="utf-8").read()
    rules = re.search(r"const RULES = `(.*?)`;", src, re.S).group(1)
    model = env("OPENAI_MODEL") or re.search(r"DEFAULT_MODEL = '([^']+)'", src).group(1)
    msgs = [m for m in (body.get("messages") or [])[-12:] if isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str)]
    if not msgs: return 400, {"error": "empty question"}
    state = dict(body.get("state") or {}); state["lang"] = body.get("lang", "en")
    payload = {"model": model, "max_completion_tokens": 900, "messages": [
        {"role": "system", "content": rules + "\n\n=== KNOWLEDGE ===\n" + str(body.get("knowledge", ""))[:160000]},
        {"role": "system", "content": "=== STATE (what the user sees right now) ===\n" + json.dumps(state, ensure_ascii=False)[:12000]},
        *[{"role": m["role"], "content": m["content"][:2000]} for m in msgs]]}
    req = urllib.request.Request(env("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: j = json.load(r)
        return 200, {"reply": j["choices"][0]["message"]["content"], "model": j.get("model"), "usage": j.get("usage")}
    except urllib.error.HTTPError as e:
        try: msg = json.load(e).get("error", {}).get("message", str(e.code))
        except Exception: msg = str(e.code)
        return 502, {"error": "OpenAI: " + msg}
    except Exception as e:
        return 502, {"error": "Could not reach OpenAI: " + str(e)}

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Expires", "0")
        super().end_headers()
    def log_message(self, *a):
        pass
    def do_POST(self):
        if self.path.split("?")[0] != "/api/chat": self.send_error(404); return
        n = int(self.headers.get("Content-Length") or 0)
        try: body = json.loads(self.rfile.read(n) or b"{}")
        except Exception: body = {}
        code, out = chat(body)
        data = json.dumps(out, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

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
