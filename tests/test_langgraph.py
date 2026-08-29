import importlib.util
import unittest

from tests.helpers import repo_tempdir

LANGGRAPH_AVAILABLE = importlib.util.find_spec("langgraph") is not None


@unittest.skipUnless(LANGGRAPH_AVAILABLE, "optional LangGraph runtime not installed")
class LangGraphTests(unittest.TestCase):
    def test_graph_interrupts_and_resumes_from_sqlite_in_new_app(self):
        from incidentlens.langgraph_adapter import resume_graph
        from incidentlens.workflow import IncidentLensApp

        with repo_tempdir() as temp:
            db = temp / "incidents.db"
            first = IncidentLensApp(db)
            paused = first.investigate("payment-unreachable", engine="langgraph", inject_failure=True)
            self.assertEqual(paused.status, "awaiting_approval")
            self.assertEqual(paused.modes["orchestration_engine"], "langgraph")
            self.assertTrue((temp / "langgraph-checkpoints.sqlite").exists())

            second = IncidentLensApp(db)
            resumed = resume_graph(second, paused.incident_id, True, "cross-process proof")
            self.assertEqual(resumed.status, "approved_pending_verification")
            self.assertEqual(resumed.reviewer_note, "cross-process proof")
            self.assertEqual(resumed.final_action, "verification_plan_only")

    def test_graph_records_recovered_trace_failure(self):
        from incidentlens.workflow import IncidentLensApp

        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("payment-unreachable", engine="langgraph", inject_failure=True)
            self.assertEqual(len(state.tool_failures), 1)
            self.assertTrue(state.tool_failures[0].recovered)


if __name__ == "__main__":
    unittest.main()

