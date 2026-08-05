import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = {
            "scenario": os.environ.get("SCENARIO_ID", "unknown"),
            "identityClientId": os.environ.get("AZURE_CLIENT_ID", ""),
            "aiServices": os.environ.get("AZURE_AI_SERVICES", ""),
            "apimEndpoint": os.environ.get("APIM_ENDPOINT", ""),
            "message": "Governed AI estate demo endpoint"
        }
        data = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()
