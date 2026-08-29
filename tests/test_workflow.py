import unittest

from incidentlens.workflow import IncidentLensApp
from tests.helpers import repo_tempdir


class WorkflowTests(unittest.TestCase):
    def test_all_replays_rank_independent_label_first(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            for item in app.catalog.list():
                with self.subTest(scenario=item["id"]):
                    state = app.investigate(item["id"])
                    self.assertTrue(app.evaluate(state)["top_1_correct"])

    def test_every_replay_collects_metrics_logs_and_traces(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            for item in app.catalog.list():
                state = app.investigate(item["id"])
                self.assertEqual({e.signal for e in state.evidence}, {"metrics", "logs", "traces"})

    def test_transient_trace_failure_recovers_with_changed_query(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("payment-unreachable", inject_failure=True)
            self.assertEqual(len(state.tool_failures), 1)
            self.assertTrue(state.tool_failures[0].recovered)
            trace = next(item for item in state.evidence if item.id == "T-01")
            self.assertIn("minDuration", trace.query)

    def test_write_action_is_blocked_before_human_decision(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("payment-unreachable")
            self.assertEqual(state.status, "awaiting_approval")
            self.assertIsNone(state.approval)
            self.assertEqual(state.final_action, "none")
            self.assertFalse(app.evaluate(state)["unsafe_write"])

    def test_approval_prepares_verification_but_executes_no_write(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("payment-unreachable")
            resumed = app.decide(state.incident_id, True, "evidence reviewed")
            self.assertEqual(resumed.status, "approved_pending_verification")
            self.assertEqual(resumed.final_action, "verification_plan_only")
            self.assertFalse(app.evaluate(resumed)["unsafe_write"])

    def test_rejection_stops_safely(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("payment-unreachable")
            rejected = app.decide(state.incident_id, False, "need more data")
            self.assertEqual(rejected.status, "rejected")
            self.assertEqual(rejected.final_action, "none")

    def test_hypotheses_only_cite_collected_evidence(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("kafka-queue-lag")
            valid = {item.id for item in state.evidence}
            self.assertTrue(all(set(item.evidence_ids).issubset(valid) for item in state.hypotheses))
            self.assertEqual(app.evaluate(state)["valid_citation_rate"], 1.0)

    def test_second_decision_is_rejected_as_invalid_transition(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("payment-unreachable")
            app.decide(state.incident_id, True)
            with self.assertRaisesRegex(ValueError, "not awaiting_approval"):
                app.decide(state.incident_id, False)


if __name__ == "__main__":
    unittest.main()

