import json
import tempfile
import unittest
from pathlib import Path

from adapter_v1 import adapt_pr


class AdapterV1Tests(unittest.TestCase):
    def test_native_outcome_fields_do_not_enter_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_dir = root / "example" / "repo"
            pr_dir = repo_dir / "prs" / "7"
            pr_dir.mkdir(parents=True)
            (repo_dir / "branches").mkdir()
            (repo_dir / "effective_rules").mkdir()

            def wrapper(path, body):
                path.write_text(json.dumps({"status": 200, "body": body}))

            pr_path = pr_dir / "pr.json"
            base_pr = {"base": {"ref": "main"}, "head": {"sha": "abc"}, "draft": False}
            wrapper(pr_path, {**base_pr, "mergeable": False, "mergeable_state": "blocked"})
            wrapper(repo_dir / "branches" / "main.json", {"protected": False, "protection": {}})
            wrapper(repo_dir / "effective_rules" / "main.json", [{
                "type": "pull_request", "ruleset_id": 1,
                "parameters": {"required_approving_review_count": 1},
            }])
            for file, body in (("reviews", []), ("check_runs", {"check_runs": []}),
                               ("combined_status", {"statuses": []}), ("commits", [])):
                wrapper(pr_dir / (file + ".json"), body)
            (pr_dir / "commit_verification.json").write_text("[]")
            before = adapt_pr(root, "example/repo", 7)
            wrapper(pr_path, {**base_pr, "mergeable": True, "mergeable_state": "clean"})
            after = adapt_pr(root, "example/repo", 7)
            self.assertEqual(before, after)
            self.assertEqual(before["predicted_native_label"], "NATIVE_BLOCKED")
            self.assertFalse(before["g4_count_eligible"])


if __name__ == "__main__":
    unittest.main()
