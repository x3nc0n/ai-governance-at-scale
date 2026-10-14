import importlib.util
import io
import json
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("demo_app", ROOT / "scenarios/shared/demo-app/app.py")
APP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APP)


class DemoAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = APP.HTTPServer(("127.0.0.1", 0), APP.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.environment = patch.dict(os.environ, {
            "SCENARIO_ID": "01-endpoint-ai",
            "KNOWLEDGE_BASE_URL": "https://example.invalid/developer-kb/invoke",
            "APIM_SUBSCRIPTION_KEY": "test-placeholder",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def request(self, body=None, path="/invoke", headers=None):
        payload = None if body is None else body if isinstance(body, bytes) else json.dumps(body).encode()
        request = urllib.request.Request(self.url + path, data=payload, headers=headers or {})
        try:
            response = urllib.request.urlopen(request, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.read()

    def test_health_and_existing_metadata(self):
        status, data = self.request(path="/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)["status"], "ok")
        status, data = self.request(path="/")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)["scenario"], "01-endpoint-ai")

    def test_post_aliases_and_response_shape(self):
        for path, field in (("/invoke", "message"), ("/chat", "prompt"), ("/", "question")):
            with self.subTest(path=path):
                status, data = self.request({field: "approved tools"}, path)
                self.assertEqual(status, 200)
                payload = json.loads(data)
                self.assertEqual(payload["mode"], "rule-based-demo")
                self.assertEqual(payload["knowledgeBase"], "developer-knowledge-base")
                self.assertIsInstance(payload["evidence"], list)

    def test_invalid_json_shapes_and_prompt_types(self):
        for body in (b"{", b"\xff", [], None, {"message": 7}, {"message": 0}, {"message": False}):
            with self.subTest(body=body):
                status, _ = self.request(b"null" if body is None else body)
                self.assertEqual(status, 400)

    def test_invalid_lengths_and_size_limit(self):
        for length in ("invalid", "-1"):
            status, _ = self.request(b"", headers={"Content-Length": length})
            self.assertEqual(status, 400)
        status, _ = self.request(b"", headers={"Content-Length": str(APP.MAX_REQUEST_BYTES + 1)})
        self.assertEqual(status, 413)
        prefix, suffix = b'{"message":"', b'"}'
        body = prefix + b"x" * (APP.MAX_REQUEST_BYTES - len(prefix) - len(suffix)) + suffix
        self.assertEqual(self.request(body)[0], 200)

    def test_unknown_post_path(self):
        self.assertEqual(self.request({}, "/missing")[0], 404)

    def test_policy_and_risk_branches(self):
        self.assertIn("governance-sensitive", APP.build_response("01-endpoint-ai", "secret")["reply"])
        self.assertIn("policy-review", APP.build_response("02-foundry-agent", "review policy")["reply"])
        self.assertIn("data-governed", APP.build_response("02-foundry-agent", "restricted data")["reply"])
        self.assertEqual(APP.build_response("04-snowflake-agent", "")["knowledgeBase"], "fallback")

    def test_broker_authenticated_upstream_contract(self):
        response = io.BytesIO(json.dumps({"reply": "sample", "evidence": ["example"]}).encode())
        with patch.object(APP.urllib.request, "urlopen", return_value=response) as open_url:
            payload = APP.build_response("03-copilot-studio", "policy")
        self.assertTrue(payload["remoteContext"])
        request = open_url.call_args.args[0]
        self.assertEqual(request.get_header("Ocp-apim-subscription-key"), "test-placeholder")
        self.assertEqual(json.loads(request.data)["message"], "policy")
        self.assertNotIn("test-placeholder", json.dumps(payload))

    def test_broker_rejects_bad_remote_payloads(self):
        payloads = (b"{", b"[]", b'{"reply":7,"evidence":[]}', b'{"reply":"x","evidence":[1]}',
                    b"x" * (APP.MAX_REQUEST_BYTES + 1))
        for body in payloads:
            with self.subTest(body_length=len(body)):
                with patch.object(APP.urllib.request, "urlopen", return_value=io.BytesIO(body)):
                    with self.assertRaises(APP.UpstreamError):
                        APP.build_studio_response("policy")

    def test_broker_rejects_missing_or_insecure_configuration(self):
        for url, key in (("", "test"), ("https://example.invalid", ""), ("http://example.invalid", "test")):
            with patch.dict(os.environ, {"KNOWLEDGE_BASE_URL": url, "APIM_SUBSCRIPTION_KEY": key}):
                with self.assertRaises(APP.UpstreamError):
                    APP.build_studio_response("policy")

    def test_broker_network_failure_returns_502_not_fallback_success(self):
        with patch.dict(os.environ, {"SCENARIO_ID": "03-copilot-studio"}):
            with patch.object(APP, "build_studio_response", side_effect=APP.UpstreamError("Upstream unavailable")):
                status, _ = self.request({"message": "policy"})
        self.assertEqual(status, 502)
        with patch.object(APP.urllib.request, "urlopen", side_effect=urllib.error.URLError("unavailable")):
            with self.assertRaises(APP.UpstreamError):
                APP.build_studio_response("policy")


class TemplateContractTests(unittest.TestCase):
    def test_examples_match_template_parameters_without_local_identifiers(self):
        for directory in sorted((ROOT / "scenarios").glob("0*/infra")):
            with self.subTest(scenario=directory.parent.name):
                template = json.loads((directory / "azuredeploy.json").read_text(encoding="utf-8"))
                examples = json.loads((directory / "main.parameters.json").read_text(encoding="utf-8"))["parameters"]
                self.assertTrue(set(examples).issubset(template["parameters"]))
                required = {key for key, value in template["parameters"].items() if "defaultValue" not in value}
                self.assertEqual(required - set(examples), {"foundationApimSubscriptionKey"} if "03-" in directory.parent.name else set())
                self.assertNotIn("foundationSubscriptionId", examples)
                self.assertEqual(examples["containerImageName"]["value"], "aigov-demo-app:latest")
                self.assertTrue(examples["foundationContainerRegistryName"]["value"].startswith("replace-with-"))
                source = (directory / "main.bicep").read_text(encoding="utf-8")
                self.assertNotIn("resourceGroup(foundationResourceGroupName)", source)

    def test_broker_key_is_a_secret_and_gateway_requires_subscription(self):
        scenario = ROOT / "scenarios/03-copilot-studio/infra"
        template = json.loads((scenario / "azuredeploy.json").read_text(encoding="utf-8"))
        self.assertEqual(template["parameters"]["foundationApimSubscriptionKey"]["type"].lower(), "securestring")
        module = (ROOT / "scenarios/01-endpoint-ai/infra/modules/developer-knowledge-apim.bicep").read_text()
        self.assertIn("subscriptionRequired: true", module)
        self.assertIn("secretRef: 'apim-subscription-key'", (scenario / "main.bicep").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
