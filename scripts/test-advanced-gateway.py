"""Offline resource-create checks only; never evidence of runtime governance."""

import copy
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "infra" / "foundation" / "advanced"
CONTRACT = json.loads((ROOT / "scripts" / "fixtures" / "advanced-gateway-contract.json").read_text())
TEMPLATE = json.loads((ENTRY / "azuredeploy.json").read_text())
PARAMETERS = json.loads((ENTRY / "main.parameters.json").read_text())
BRANCH = "x3nc0n-blog-announcement-integration"


def validate_request(value, schema, path="resource"):
    if schema.get("readOnly"):
        raise ValueError(f"{path} is read-only")
    expected = {"object": dict, "string": str}[schema["type"]]
    if not isinstance(value, expected):
        raise ValueError(f"{path} must be {schema['type']}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path} is not an allowed enum value")
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                raise ValueError(f"{path}.{required} is required")
        fields = schema.get("properties", {})
        for key, item in value.items():
            child = fields.get(key, schema.get("additionalProperties"))
            if child is None:
                raise ValueError(f"{path}.{key} is outside the pinned request subset")
            validate_request(item, child, f"{path}.{key}")


class AdvancedGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = TEMPLATE["resources"]["gateway"]

    def request(self):
        # name/type/apiVersion are ARM envelope fields, not writable REST body fields.
        request = {k: copy.deepcopy(v) for k, v in self.resource.items() if k not in ("name", "type", "apiVersion")}
        for field in ("location", "tags"):
            if request.get(field) == f"[parameters('{field}')]":
                request[field] = copy.deepcopy(TEMPLATE["parameters"][field]["defaultValue"])
        return request

    def test_pinned_compiler_and_resource_group_envelope(self):
        self.assertEqual(TEMPLATE["$schema"], "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#")
        self.assertEqual(TEMPLATE["metadata"]["_generator"]["version"], "0.44.1.10279")
        self.assertEqual(TEMPLATE["languageVersion"], "2.0")
        self.assertEqual(len(TEMPLATE["resources"]), 1)
        self.assertEqual(self.resource["type"], CONTRACT["resourceType"])
        self.assertEqual(self.resource["apiVersion"], CONTRACT["apiVersion"])
        self.assertEqual(CONTRACT["sourceCommit"], "2335fe5db98171e7a78d08e712920b1869c536ce")

    def test_minimal_create_request_against_pinned_projection(self):
        validate_request(self.request(), CONTRACT["request"])
        self.assertEqual(set(self.request()), {"location", "tags", "sku", "identity", "properties"})
        self.assertEqual(self.resource["properties"], {})
        self.assertEqual(self.resource["sku"], {"name": CONTRACT["exampleSkuName"]})
        self.assertEqual(self.resource["identity"], {"type": "SystemAssigned"})

    def test_required_fields_and_wrong_types_rejected(self):
        for field in ("location", "properties"):
            request = self.request()
            del request[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_request(request, CONTRACT["request"])
        for field, value in (("properties", []), ("identity", {"type": "AppOnly"}), ("sku", {}), ("tags", {"unsafe": 123})):
            request = self.request()
            request[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_request(request, CONTRACT["request"])

    def test_readonly_and_invented_controls_rejected(self):
        for location, field, value in (
            ((), "eTag", "response-only"), ((), "systemData", {}),
            (("identity",), "principalId", "response-only"),
            (("identity",), "tenantId", "response-only"),
            (("properties",), "frontend", {"defaultHostname": "not-an-input"}),
            (("properties",), "provisioningState", "Succeeded"),
            (("properties",), "toolServers", []),
            (("properties",), "threatProtectionMode", "Block"),
        ):
            request = copy.deepcopy(self.request())
            target = request
            for part in location:
                target = target[part]
            target[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_request(request, CONTRACT["request"])

    def test_optional_network_contract_is_not_a_protection_claim(self):
        schema = CONTRACT["request"]["properties"]["properties"]
        self.assertNotIn("required", schema)
        self.assertEqual(CONTRACT["createOnly"], ["location", "properties.backend"])
        self.assertEqual(CONTRACT["subnetDelegation"], "Microsoft.App/environments")
        request = self.request()
        request["properties"] = {"backend": {"subnet": {}}}
        with self.assertRaises(ValueError):
            validate_request(request, CONTRACT["request"])
        self.assertNotIn("backend", self.resource["properties"])

    def test_default_and_explicit_name_contract(self):
        parameter = TEMPLATE["parameters"]["gatewayName"]
        self.assertEqual(parameter["minLength"], 3)
        self.assertEqual(parameter["maxLength"], 24)
        self.assertEqual(parameter["defaultValue"], "[format('aigw-{0}', uniqueString(resourceGroup().id))]")
        self.assertEqual(self.resource["name"], "[parameters('gatewayName')]")
        self.assertIn(CONTRACT["namePattern"], parameter["metadata"]["description"])
        for name in ("aigw-0123456789abc", "aigw-synthetic-demo", "abc", "a" * 24):
            self.assertRegex(name, CONTRACT["namePattern"])
        for name in ("ab", "a" * 25, "UpperCase", "-aigw", "aigw-", "a/b"):
            self.assertIsNone(re.fullmatch(CONTRACT["namePattern"], name))
        self.assertNotIn("gatewayName", PARAMETERS["parameters"])

    def test_region_tags_and_safe_parameter_example(self):
        params = TEMPLATE["parameters"]
        self.assertEqual(set(params), {"location", "gatewayName", "tags"})
        self.assertEqual(params["location"]["defaultValue"], "eastus2")
        self.assertEqual(params["location"]["allowedValues"], ["eastus2", "swedencentral"])
        self.assertEqual(self.resource["location"], "[parameters('location')]")
        self.assertEqual(self.resource["tags"], "[parameters('tags')]")
        self.assertEqual(PARAMETERS["parameters"]["location"]["value"], "eastus2")
        self.assertEqual(set(PARAMETERS["parameters"]), {"location", "tags"})
        self.assertTrue(all(isinstance(v, str) for v in PARAMETERS["parameters"]["tags"]["value"].values()))
        self.assertEqual(TEMPLATE["parameters"]["tags"]["$ref"], "#/definitions/gatewayTags")
        self.assertEqual(TEMPLATE["definitions"]["gatewayTags"]["additionalProperties"], {"type": "string"})

    def test_only_nonsecret_outputs_no_guessed_endpoint(self):
        self.assertEqual(set(TEMPLATE["outputs"]), {"gatewayResourceId", "gatewayResourceName", "gatewayApiVersion"})
        self.assertEqual(TEMPLATE["outputs"]["gatewayApiVersion"]["value"], CONTRACT["apiVersion"])
        self.assertEqual(TEMPLATE["outputs"]["gatewayResourceName"]["value"], "[parameters('gatewayName')]")
        self.assertEqual(TEMPLATE["outputs"]["gatewayResourceId"]["value"], "[resourceId('Microsoft.ApiManagement/aigateways', parameters('gatewayName'))]")
        text = json.dumps(TEMPLATE) + json.dumps(PARAMETERS)
        self.assertNotRegex(text, r"(?i)listKeys|listSecrets|tenantId|principalId|password|clientSecret|api-key|accessToken|azure-api\.net|@")
        self.assertNotRegex(text, r"(?i)[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")
        self.assertNotIn("Microsoft.ApiManagement/service", text)

    def test_button_decodes_to_existing_branch_template(self):
        readme = (ENTRY / "README.md").read_text(encoding="utf-8")
        targets = re.findall(r"https://portal\.azure\.com/#create/Microsoft\.Template/uri/([^)\s]+)", readme)
        self.assertEqual(len(targets), 1)
        decoded = unquote(targets[0])
        expected = f"https://raw.githubusercontent.com/x3nc0n/ai-governance-at-scale/{BRANCH}/infra/foundation/advanced/azuredeploy.json"
        self.assertEqual(decoded, expected)
        self.assertEqual(urlparse(decoded).scheme, "https")
        self.assertTrue(ENTRY.joinpath("azuredeploy.json").is_file())
        self.assertIn("Branch-bound pending merge", readme)
        self.assertIn("infra/foundation/advanced/README.md", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_ci_covers_compile_drift_and_static_suite(self):
        build = (ROOT / ".github" / "workflows" / "bicep-compile.yml").read_text()
        self.assertIn("az bicep install --version v0.44.1", build)
        self.assertIn("--file infra/foundation/advanced/main.bicep --outfile infra/foundation/advanced/azuredeploy.json", build)
        drift = next(line for line in build.splitlines() if "git diff --exit-code" in line)
        self.assertIn("infra/foundation/advanced/azuredeploy.json", drift)
        self.assertIn("--file infra/foundation/advanced/test-deployment.bicep --outfile infra/foundation/advanced/test-deployment.json", build)
        self.assertIn("infra/foundation/advanced/test-deployment.json", drift)
        self.assertIn("python -B scripts/test-advanced-gateway.py", (ROOT / ".github" / "workflows" / "squad-ci.yml").read_text())

    def test_subscription_wrapper_only_creates_isolated_group_and_gateway(self):
        wrapper = json.loads((ENTRY / "test-deployment.json").read_text())
        self.assertEqual(wrapper["$schema"], "https://schema.management.azure.com/schemas/2018-05-01/subscriptionDeploymentTemplate.json#")
        self.assertEqual(wrapper["metadata"]["_generator"]["version"], "0.44.1.10279")
        self.assertEqual(set(wrapper["resources"]), {"testGroup", "gateway"})
        self.assertNotIn("defaultValue", wrapper["parameters"]["resourceGroupName"])
        group = wrapper["resources"]["testGroup"]
        self.assertEqual(group["type"], "Microsoft.Resources/resourceGroups")
        self.assertEqual(group["name"], "[parameters('resourceGroupName')]")
        self.assertEqual(group["tags"], "[parameters('tags')]")
        module = wrapper["resources"]["gateway"]
        self.assertEqual(module["type"], "Microsoft.Resources/deployments")
        self.assertEqual(module["resourceGroup"], "[parameters('resourceGroupName')]")
        self.assertEqual(module["dependsOn"], ["testGroup"])
        self.assertEqual(module["properties"]["mode"], "Incremental")
        self.assertEqual(module["properties"]["template"], TEMPLATE)
        self.assertEqual(set(module["properties"]["parameters"]), {"location", "tags"})
        self.assertNotRegex(json.dumps(wrapper), r"(?i)listKeys|listSecrets|roleAssignments|tenantId|principalId|password|clientSecret|accessToken|@")
        self.assertNotRegex(json.dumps(wrapper), r"(?i)[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")


if __name__ == "__main__":
    unittest.main()
