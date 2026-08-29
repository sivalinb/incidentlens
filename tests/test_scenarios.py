import json
import unittest
from pathlib import Path

from incidentlens.scenarios import ScenarioCatalog


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.catalog = ScenarioCatalog()

    def test_catalog_lists_three_scenarios(self):
        self.assertEqual(len(self.catalog.list()), 3)

    def test_operational_fixtures_do_not_contain_evaluator_answers(self):
        root = Path("incidentlens/scenarios")
        for path in root.glob("*.json"):
            with self.subTest(path=path):
                data = json.loads(path.read_text())
                serialized = json.dumps(data).lower()
                self.assertNotIn("ground_truth", serialized)
                self.assertNotIn("expected_cause", serialized)
                self.assertNotIn('"hypotheses"', serialized)

    def test_all_signals_use_real_units_and_timestamped_values(self):
        units = {"payment-unreachable": "percent", "email-memory-leak": "MiB", "kafka-queue-lag": "messages"}
        for scenario_id, unit in units.items():
            with self.subTest(scenario=scenario_id):
                metric = self.catalog.load(scenario_id)["metrics"]
                self.assertEqual(metric["unit"], unit)
                self.assertTrue(all("timestamp" in item and "value" in item for item in metric["values"]))

    def test_email_scenario_uses_valid_log_evidence_id(self):
        scenario = self.catalog.load("email-memory-leak")
        self.assertEqual(scenario["logs"]["id"], "L-01")

    def test_unknown_scenario_has_actionable_error(self):
        with self.assertRaisesRegex(ValueError, "Choose one of"):
            self.catalog.load("does-not-exist")


if __name__ == "__main__":
    unittest.main()

