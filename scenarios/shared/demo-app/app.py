import json
import os
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_REQUEST_BYTES = 64 * 1024


class UpstreamError(Exception):
    pass


KNOWLEDGE = {
    "approved_tools": [
        "Microsoft 365 Copilot", "Azure AI Foundry", "Microsoft Purview", "Defender for AI Services"
    ],
    "policies": [
        "Only approved tools may access restricted data.",
        "Sensitive prompts should be routed through the governed estate.",
        "Every request should include an agent identity and correlation context."
    ],
    "risk_signals": [
        "Prompt contains secret material or regulated content.",
        "The user is requesting broad data export outside approved tools.",
        "The request would bypass the governance gateway."
    ],
}


def build_response(scenario_id, prompt):
    prompt_text = (prompt or "").strip().lower()
    if scenario_id == "01-endpoint-ai":
        return build_developer_response(prompt_text)
    if scenario_id == "02-foundry-agent":
        return build_foundry_response(prompt_text)
    if scenario_id == "03-copilot-studio":
        return build_studio_response(prompt_text)
    return build_default_response(prompt_text)


def build_developer_response(prompt_text):
    if "tool" in prompt_text or "approved" in prompt_text:
        reply = "The demo catalog lists Microsoft 365 Copilot, Azure AI Foundry, Microsoft Purview, and Defender for AI Services. Replace this sample catalog with your organization's approved services."
        evidence = ["Use an approved tool catalog.", "Configure correlated logging and identity checks before handling real data."]
    elif "risk" in prompt_text or "sensitive" in prompt_text or "secret" in prompt_text:
        reply = "The developer agent flags the request as a governance-sensitive prompt and recommends routing it through the governed gateway with an identity-aware policy check."
        evidence = KNOWLEDGE["risk_signals"]
    else:
        reply = "The developer agent is ready to answer governance questions about approved tools, sensitive prompts, and identity requirements."
        evidence = KNOWLEDGE["policies"]
    return {
        "agentType": "developer-governance-assistant",
        "reply": reply,
        "evidence": evidence,
        "knowledgeBase": "developer-knowledge-base"
    }


def build_foundry_response(prompt_text):
    if "policy" in prompt_text or "review" in prompt_text:
        reply = "The Foundry agent recommends a policy-review workflow: classify the prompt, apply the approved-tools policy, and route the request through APIM with correlated logging."
        evidence = KNOWLEDGE["policies"]
    elif "data" in prompt_text or "restricted" in prompt_text:
        reply = "The Foundry agent classifies the request as data-governed and recommends using only approved data access channels with Purview labels in place."
        evidence = ["Purview labels should be evaluated before data access.", "The request should be tied to an agent identity and monitored by Defender for AI Services."]
    else:
        reply = "The Foundry agent is ready to review prompt safety and data handling posture for the governed estate."
        evidence = KNOWLEDGE["policies"]
    return {
        "agentType": "foundry-policy-review-agent",
        "reply": reply,
        "evidence": evidence,
        "knowledgeBase": "foundry-policy-review"
    }


def build_studio_response(prompt_text):
    remote_url = os.environ.get("KNOWLEDGE_BASE_URL", "")
    subscription_key = os.environ.get("APIM_SUBSCRIPTION_KEY", "")
    if not remote_url or not subscription_key:
        raise UpstreamError("Knowledge base URL and APIM subscription key must be configured.")
    try:
        parsed_url = urllib.parse.urlsplit(remote_url)
        if parsed_url.scheme != "https" or not parsed_url.hostname or parsed_url.username or parsed_url.password:
            raise UpstreamError("Knowledge base URL must use HTTPS without embedded credentials.")
        payload = json.dumps({"message": prompt_text or "Summarize the governance posture."}).encode("utf-8")
        request = urllib.request.Request(
            remote_url, data=payload,
            headers={"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": subscription_key},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            remote_bytes = response.read(MAX_REQUEST_BYTES + 1)
        if len(remote_bytes) > MAX_REQUEST_BYTES:
            raise UpstreamError("Knowledge base response exceeds the size limit.")
        remote_payload = json.loads(remote_bytes.decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, UnicodeDecodeError) as error:
        raise UpstreamError("Knowledge base request failed or returned invalid JSON.") from error
    if not isinstance(remote_payload, dict):
        raise UpstreamError("Knowledge base response must be a JSON object.")
    remote_reply = remote_payload.get("reply")
    remote_evidence = remote_payload.get("evidence")
    if not isinstance(remote_reply, str) or not isinstance(remote_evidence, list) or not all(isinstance(item, str) for item in remote_evidence):
        raise UpstreamError("Knowledge base response must contain a reply and string evidence list.")
    return {
        "agentType": "copilot-studio-governance-agent",
        "reply": f"The broker received knowledge base context: {remote_reply}",
        "evidence": remote_evidence + ["The broker called its configured knowledge base endpoint."],
        "knowledgeBase": "studio-broker",
        "remoteContext": True,
    }


def build_default_response(prompt_text):
    return {
        "agentType": "governed-agent",
        "reply": "The governed estate agent is ready to process requests using the shared governance plane.",
        "evidence": KNOWLEDGE["policies"],
        "knowledgeBase": "fallback"
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/health":
            body = {
                "status": "ok",
                "scenario": os.environ.get("SCENARIO_ID", "unknown"),
                "agentRole": os.environ.get("SCENARIO_LABEL", "governed-agent"),
                "identityClientId": os.environ.get("AZURE_CLIENT_ID", ""),
                "aiServices": os.environ.get("AZURE_AI_SERVICES", ""),
                "apimEndpoint": os.environ.get("APIM_ENDPOINT", ""),
                "message": "Governed AI estate agent endpoint"
            }
        else:
            body = {
                "scenario": os.environ.get("SCENARIO_ID", "unknown"),
                "agentRole": os.environ.get("SCENARIO_LABEL", "governed-agent"),
                "identityClientId": os.environ.get("AZURE_CLIENT_ID", ""),
                "aiServices": os.environ.get("AZURE_AI_SERVICES", ""),
                "apimEndpoint": os.environ.get("APIM_ENDPOINT", ""),
                "message": "Governed AI estate agent endpoint"
            }
        data = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = urllib.parse.urlsplit(self.path).path
        if path not in ["/invoke", "/chat", "/"]:
            self.send_response(404)
            self.end_headers()
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return
        if content_length < 0:
            self.send_error(400, "Invalid Content-Length")
            return
        if content_length > MAX_REQUEST_BYTES:
            self.send_error(413, "Request body too large")
            return
        body_bytes = self.rfile.read(content_length) if content_length else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "Request body must be valid UTF-8 JSON")
            return
        if not isinstance(body, dict):
            self.send_error(400, "Request body must be a JSON object")
            return
        prompt = next((body[field] for field in ("message", "prompt", "question") if field in body and body[field] is not None and body[field] != ""), "")
        if not isinstance(prompt, str):
            self.send_error(400, "Prompt must be a string")
            return
        try:
            payload = build_response(os.environ.get("SCENARIO_ID", "unknown"), prompt)
        except UpstreamError as error:
            self.log_error("%s", error)
            self.send_error(502, str(error))
            return
        payload.update({
            "mode": "rule-based-demo",
            "scenario": os.environ.get("SCENARIO_ID", "unknown"),
            "identityClientId": os.environ.get("AZURE_CLIENT_ID", ""),
            "aiServices": os.environ.get("AZURE_AI_SERVICES", ""),
            "apimEndpoint": os.environ.get("APIM_ENDPOINT", ""),
            "knowledgeBaseUrl": os.environ.get("KNOWLEDGE_BASE_URL", "")
        })
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()
