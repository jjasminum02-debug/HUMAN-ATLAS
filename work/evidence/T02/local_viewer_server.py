#!/usr/bin/env python3
"""Task-local static viewer server with one fixed-path PNG evidence endpoint."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3]
OUT=(ROOT/"work/evidence/T02/calf-viewer-trial.png").resolve()
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_POST(self):
        if self.path != "/__capture":
            self.send_error(404); return
        length=int(self.headers.get("Content-Length","0"))
        if length < 8 or length > 8*1024*1024:
            self.send_error(413); return
        data=self.rfile.read(length)
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            self.send_error(415); return
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_bytes(data)
        body=json.dumps({"saved":True,"bytes":len(data),"path":str(OUT)}).encode()
        self.send_response(200);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,fmt,*args):
        print("viewer-server "+fmt%args,flush=True)

if __name__=="__main__":
    print(f"Serving {ROOT} at http://127.0.0.1:8765",flush=True)
    ThreadingHTTPServer(("127.0.0.1",8765),Handler).serve_forever()
