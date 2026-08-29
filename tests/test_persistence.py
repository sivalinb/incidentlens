import unittest

from incidentlens.persistence import IncidentStore
from incidentlens.workflow import IncidentLensApp
from tests.helpers import repo_tempdir


class PersistenceTests(unittest.TestCase):
    def test_round_trip_preserves_typed_state(self):
        with repo_tempdir() as temp:
            app = IncidentLensApp(temp / "incidents.db")
            state = app.investigate("email-memory-leak")
            loaded = IncidentStore(temp / "incidents.db").load(state.incident_id)
            self.assertEqual(loaded.to_dict(), state.to_dict())

    def test_new_app_process_can_resume_native_incident(self):
        with repo_tempdir() as temp:
            db = temp / "incidents.db"
            first = IncidentLensApp(db)
            state = first.investigate("payment-unreachable")
            second = IncidentLensApp(db)
            resumed = second.decide(state.incident_id, True, "second process")
            self.assertEqual(resumed.reviewer_note, "second process")

    def test_missing_incident_raises_key_error(self):
        with repo_tempdir() as temp:
            store = IncidentStore(temp / "incidents.db")
            with self.assertRaises(KeyError):
                store.load("IL-MISSING")


if __name__ == "__main__":
    unittest.main()

