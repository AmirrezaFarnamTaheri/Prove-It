import json
import tempfile
import unittest
from pathlib import Path

from prove_it.composer import ProveItError, compose, load_manifest, run_static_case, validate_prompt


ROOT = Path(__file__).resolve().parents[1]


class ComposerTests(unittest.TestCase):
    def test_manifest_fragments_exist(self):
        manifest = load_manifest(ROOT)
        paths = [manifest["core"]]
        for group in ("profiles", "templates", "adapters"):
            paths.extend(meta["path"] for meta in manifest[group].values())
        missing = [path for path in paths if not (ROOT / path).is_file()]
        self.assertEqual([], missing)

    def test_composition_orders_adapter_core_profile_template_task(self):
        task = {"objective": "Review authentication handling", "deliverables": ["Findings"]}
        result = compose(
            ROOT,
            task,
            template="audit",
            profiles=["security", "audit-remediation"],
            adapter="generic",
        )
        text = result.text
        self.assertLess(text.index("<adapter>"), text.index("<role>"))
        self.assertLess(text.index("<role>"), text.index("<security_profile>"))
        self.assertLess(text.index("<security_profile>"), text.index("<audit_profile>"))
        self.assertLess(text.index("<audit_profile>"), text.index("<task_mode>"))
        self.assertLess(text.index("<task_mode>"), text.index("<task>"))
        self.assertEqual([], validate_prompt(text))

    def test_duplicate_profiles_are_deduplicated(self):
        task = {"objective": "Harden input validation"}
        result = compose(ROOT, task, profiles=["security", "security"])
        self.assertEqual(1, result.text.count("<security_profile>"))
        self.assertEqual(("security",), result.profiles)

    def test_unknown_profile_rejected(self):
        with self.assertRaises(ProveItError):
            compose(ROOT, {"objective": "x"}, profiles=["does-not-exist"])

    def test_validate_detects_placeholders(self):
        prompt = compose(ROOT, {"objective": "Ship feature"}).text + "\n[INSERT SOMETHING]\n"
        errors = validate_prompt(prompt)
        self.assertTrue(any("unresolved placeholder" in item for item in errors))

    def test_static_eval_fixture(self):
        case = {
            "task": {"objective": "Audit auth"},
            "template": "audit",
            "profiles": ["security"],
            "required_substrings": ["<security_profile>", "<task>"],
            "forbidden_substrings": ["[INSERT"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            self.assertEqual([], run_static_case(ROOT, path))


if __name__ == "__main__":
    unittest.main()
