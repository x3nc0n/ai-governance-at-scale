"""Focused text/fixture regressions, not a KQL parser or tenant execution."""

from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "scenarios" / "01-endpoint-ai" / "hunting"
CORE = sorted(PACK.glob("[0-9][0-9]-*.kql"))


def function_body(query, name):
    match = re.search(rf"let {name} = .*?\{{(.*?)\n\}};", query, re.S)
    if not match:
        raise AssertionError(f"Missing standalone function {name}")
    return match.group(1)


class HuntingPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queries = {path.name[:2]: path.read_text(encoding="utf-8") for path in CORE}
        cls.destination = cls.queries["05"]
        cls.host_fixture = (PACK / "validation" / "host-boundaries.kql").read_text(encoding="utf-8")

    def test_candidate_file_and_documentation_coverage(self):
        self.assertEqual(list(self.queries), [f"{n:02d}" for n in range(1, 11)])
        readme = (PACK / "README.md").read_text(encoding="utf-8")
        for n in range(1, 12):
            self.assertRegex(readme, rf"\| {n} \|")
        for path in PACK.rglob("*.kql"):
            self.assertIn(path.relative_to(PACK).as_posix(), readme)
            self.assertTrue(path.read_text(encoding="utf-8").endswith("\n"))
        self.assertIn("(hunting/README.md)", (PACK.parent / "README.md").read_text(encoding="utf-8"))

    def test_added_file_whitespace(self):
        for path in [*PACK.rglob("*"), Path(__file__)]:
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.endswith("\n"), str(path))
                for number, line in enumerate(text.splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path}:{number}")

    def test_standalone_evidence_and_matching_boundaries(self):
        baseline = function_body(self.queries["01"], "Evidence")
        ai_text = re.search(r'let AiText = @"(.*?)";', self.queries["01"]).group(1)
        pattern = re.compile(ai_text)
        names = set(re.findall(r'"([^"]+)"', baseline.split("),")[0]))
        for query in self.queries.values():
            self.assertEqual(function_body(query, "Evidence"), baseline)
            self.assertIn(f'let AiText = @"{ai_text}";', query)
            self.assertNotIn("has_any", query)
        for text in ["lmstudio", "C:\\Apps\\lm-studio\\node.exe", "LM Studio", "@anthropic-ai/claude-code"]:
            self.assertIsNotNone(pattern.search(text), text)
        for text in ["aclaude", "openaiish", "scursor", "roo", "poe", "goose", "warp", "devin"]:
            self.assertIsNone(pattern.search(text), text)
        self.assertIn("claude.exe", names)
        self.assertIn("lm-studio", names)
        for generic in ["node", "python", "electron", "git"]:
            self.assertNotIn(generic, names)
        self.assertIn('"image-name-candidate"', baseline)
        self.assertIn('"path-or-commandline-candidate"', baseline)

    def test_host_boundaries_and_shared_fixture_helpers(self):
        for name in ["NormalizeHost", "IsAiDestination"]:
            self.assertEqual(
                function_body(self.destination, name),
                function_body(self.host_fixture, name),
            )
        normalize = function_body(self.destination, "NormalizeHost")
        for required in ['parse_url(absolute).Host', 'tolower(', 'trim_end(', 'value startswith "//"']:
            self.assertIn(required, normalize)
        predicate = function_body(self.destination, "IsAiDestination")
        exact = set(re.findall(r'"([^"]+)"', predicate.split("or host")[0]))
        suffixes = set(re.findall(r'endswith "([^"]+)"', predicate))
        self.assertEqual(suffixes, {"." + host for host in exact})
        self.assertNotIn("github.com", exact)
        self.assertNotIn("googleapis.com", exact)
        fixtures = re.findall(r'^\s*"([^"]*)", (true|false)', self.host_fixture, re.M)
        self.assertGreaterEqual(len(fixtures), 17)
        for raw, expected in fixtures:
            with self.subTest(raw=raw):
                value = raw.strip()
                absolute = "https:" + value if value.startswith("//") else (
                    value if "://" in value else "https://" + value
                )
                host = (urlsplit(absolute).hostname or "").lower().rstrip(".")
                actual = host in exact or any(host.endswith(suffix) for suffix in suffixes)
                self.assertEqual(actual, expected == "true")
        self.assertIn("| where Actual != Expected", self.host_fixture)

    def test_event_identifiers_and_actor_accounts(self):
        for key in ["01", "02", "03", "04", "06", "07", "08", "09"]:
            query = self.queries[key]
            projection = query.rsplit("| project ", 1)[1]
            for field in ["Timestamp", "DeviceId", "DeviceName", "ReportId"]:
                self.assertRegex(projection, rf"\b{field}\b", key)
                self.assertNotRegex(query, rf"\b{field}\s*=", key)
            self.assertIn("InitiatingProcessAccountUpn", projection)
        for key in ["01", "02", "03"]:
            self.assertRegex(self.queries[key].rsplit("| project ", 1)[1], r"\bAccountUpn\b")
        for key in ["04", "07", "08", "09"]:
            self.assertNotRegex(self.queries[key], r"(?<!InitiatingProcess)\bAccountUpn\b")
        for key in ["05", "10"]:
            self.assertIn("Hunting summary only", self.queries[key])
            self.assertIn("| summarize", self.queries[key])
            for args in re.findall(r"make_set\(([^)]*)\)", self.queries[key]):
                self.assertRegex(args, r", 20$")
            self.assertNotIn("dcountif(", self.queries[key])
        self.assertIn("dcount(AccountUpn)", self.queries["10"])
        self.assertNotIn("dcount(InitiatingProcessAccountUpn)", self.queries["10"])

    def test_direct_parent_and_file_write_scope(self):
        for key in ["02", "03"]:
            query = self.queries[key]
            self.assertIn(
                "ParentEvidence = Evidence(InitiatingProcessFileName, InitiatingProcessFolderPath, InitiatingProcessCommandLine)",
                query,
            )
            self.assertIn('| where ParentEvidence != "none"', query)
            self.assertNotIn("Evidence(FileName", query)
            self.assertIn('"pwsh.exe", "pwsh"', query)
        self.assertNotIn("RemoteUrl", self.queries["02"])
        self.assertNotIn("RemoteUrl", self.queries["03"])
        self.assertNotIn("or RemoteUrl", self.queries["04"])
        writes = self.queries["08"]
        self.assertIn('ActionType in ("FileCreated", "FileModified", "FileRenamed")', writes)
        self.assertIn("or PreviousFileName matches regex", writes)
        extension = re.compile(re.search(r'FileName matches regex @"(.*?)"', writes).group(1))
        for name in ["run.ps1", "RUN.EXE", "script.py", "module.dll"]:
            self.assertIsNotNone(extension.search(name))
        for name in ["run.ps1.txt", "no-extension", "report.json"]:
            self.assertIsNone(extension.search(name))

    def test_correlation_identity_deduplication_and_fixture(self):
        query = self.queries["06"]
        self.assertIn("join kind=inner (Candidates) on DeviceId, ActorPid, ActorCreated", query)
        self.assertIn("summarize arg_min(CreatedEventTime, *) by DeviceId, ActorPid, ActorCreated", query)
        self.assertIn("ActorPid = ProcessId, ActorCreated = ProcessCreationTime", query)
        self.assertIn("ActorPid = InitiatingProcessId, ActorCreated = InitiatingProcessCreationTime", query)
        self.assertIn("isnotnull(ProcessCreationTime)", query)
        self.assertIn("isnotnull(InitiatingProcessCreationTime)", query)
        self.assertIn("Timestamp >= ActorCreated", query)
        self.assertNotIn("ago(4h)", query)
        projection = query.rsplit("| project ", 1)[1]
        self.assertIn("CreatedAccountUpn", projection)
        self.assertIn("CreatedDeviceName", projection)
        self.assertNotRegex(projection, r"\b(DeviceName1|AccountUpn1|Timestamp1|ReportId1)\b")
        # Model only the documented composite-key join and deduplication contract.
        creations = [
            ("device-a", 42, 10, 10, "original"),
            ("device-a", 42, 10, 11, "duplicate"),
            ("device-a", 42, 30, 30, "pid-reused"),
            ("device-b", 42, 10, 10, "other-device"),
            ("device-a", 43, None, 10, "missing-creation"),
        ]
        unique = {}
        for device, pid, created, event_time, label in creations:
            if not device or pid <= 0 or created is None:
                continue
            key = (device, pid, created)
            if key not in unique or event_time < unique[key][0]:
                unique[key] = (event_time, label)
        networks = [
            ("device-a", 42, 10, 20, 101),
            ("device-a", 42, 10, 21, 102),
            ("device-a", 42, 25, 31, 103),
            ("device-c", 42, 10, 20, 104),
            ("device-a", 43, None, 20, 105),
            ("device-a", 42, 30, 29, 106),
            ("device-a", 42, 30, 40, 107),
        ]
        matches = [
            (report_id, unique[(device, pid, created)][1])
            for device, pid, created, event_time, report_id in networks
            if created is not None and (device, pid, created) in unique and event_time >= created
        ]
        self.assertEqual(matches, [(101, "original"), (102, "original"), (107, "pid-reused")])

    def test_preview_does_not_assume_agent_labels_or_device_mapping(self):
        for path in (PACK / "preview").glob("*.kql"):
            query = path.read_text(encoding="utf-8")
            executable_lines = "\n".join(line for line in query.splitlines() if not line.startswith("//"))
            self.assertNotIn("endpointAiAgent", executable_lines)
            self.assertNotIn("runs on", executable_lines)
            self.assertNotIn("DeviceId", executable_lines)
            self.assertNotIn("DeviceProcessEvents", executable_lines)
            self.assertNotIn("join", executable_lines)
        self.assertIn("EntityIds", (PACK / "preview" / "11-exposure-graph-identifiers.kql").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
