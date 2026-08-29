from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

from tests.helpers import repo_tempdir


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["LANGGRAPH_STRICT_MSGPACK"] = "true"
    return subprocess.run(
        [sys.executable, "-m", "incidentlens", *args],
        cwd=os.getcwd(),
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


class CliEndToEndTests(unittest.TestCase):
    def test_native_cli_investigates_and_resumes_from_persisted_state(self):
        with repo_tempdir() as temp:
            db = str(temp / "native.db")
            investigated = run_cli(
                "--db", db, "investigate", "payment-unreachable", "--inject-failure", "--json"
            )
            self.assertEqual(investigated.returncode, 0, investigated.stderr)
            paused = json.loads(investigated.stdout)
            self.assertEqual(paused["status"], "awaiting_approval")
            self.assertTrue(paused["tool_failures"][0]["recovered"])

            resumed = run_cli(
                "--db", db, "resume", paused["incident_id"], "--approve", "--note", "CLI reviewer", "--json"
            )
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            approved = json.loads(resumed.stdout)
            self.assertEqual(approved["status"], "approved_pending_verification")
            self.assertEqual(approved["final_action"], "verification_plan_only")
            self.assertEqual(approved["reviewer_note"], "CLI reviewer")

    def test_langgraph_cli_resumes_checkpoint_in_a_second_process(self):
        with repo_tempdir() as temp:
            db = str(temp / "langgraph.db")
            investigated = run_cli(
                "--db", db, "investigate", "payment-unreachable", "--engine", "langgraph",
                "--inject-failure", "--json",
            )
            self.assertEqual(investigated.returncode, 0, investigated.stderr)
            paused = json.loads(investigated.stdout)
            self.assertEqual(paused["status"], "awaiting_approval")

            resumed = run_cli(
                "--db", db, "resume", paused["incident_id"], "--engine", "langgraph",
                "--approve", "--note", "cross-process CLI proof", "--json",
            )
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            approved = json.loads(resumed.stdout)
            self.assertEqual(approved["status"], "approved_pending_verification")
            self.assertEqual(approved["reviewer_note"], "cross-process CLI proof")

    def test_langgraph_inline_approval_finishes_the_checkpoint(self):
        with repo_tempdir() as temp:
            result = run_cli(
                "--db", str(temp / "inline.db"), "investigate", "payment-unreachable",
                "--engine", "langgraph", "--approve", "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(result.stdout)
            self.assertEqual(state["status"], "approved_pending_verification")
            self.assertEqual(state["final_action"], "verification_plan_only")

    def test_evaluate_command_passes_all_three_independent_labels(self):
        with repo_tempdir() as temp:
            result = run_cli("--db", str(temp / "evaluate.db"), "evaluate")
            self.assertEqual(result.returncode, 0, result.stderr)
            for scenario in ("email-memory-leak", "kafka-queue-lag", "payment-unreachable"):
                self.assertIn(scenario, result.stdout)
            self.assertEqual(result.stdout.count("'valid_citation_rate': 1.0"), 3)
            self.assertEqual(result.stdout.count("'unsafe_write': False"), 3)


if __name__ == "__main__":
    unittest.main()
