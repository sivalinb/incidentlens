import json
import os
import unittest
from unittest.mock import patch

from incidentlens.llm import LLMContractError, OpenAICompatibleHypothesisEngine
from incidentlens.models import Evidence


def evidence():
    return [
        Evidence("M-01", "metrics", "test", "q1", "metric evidence", {}),
        Evidence("L-01", "logs", "test", "q2", "log evidence", {}),
        Evidence("T-01", "traces", "test", "q3", "trace evidence", {}),
    ]


def response(hypotheses):
    payload = {"choices": [{"message": {"content": json.dumps({"hypotheses": hypotheses})}}]}
    return json.dumps(payload).encode()


class LLMTests(unittest.TestCase):
    env = {"LLM_BASE_URL": "https://provider.example/v1", "LLM_API_KEY": "secret", "LLM_MODEL": "model"}

    def valid_items(self):
        return [
            {"cause": f"cause {i}", "confidence": 0.9 - i / 10, "verdict": "supported", "evidence_ids": ["M-01", "L-01"], "rationale": "because"}
            for i in range(3)
        ]

    def test_missing_configuration_fails_without_network(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(LLMContractError, "Set LLM_BASE_URL"):
                OpenAICompatibleHypothesisEngine()

    def test_valid_response_returns_three_sorted_hypotheses(self):
        with patch.dict(os.environ, self.env, clear=True):
            engine = OpenAICompatibleHypothesisEngine(transport=lambda _: response(self.valid_items()))
            result = engine.generate({"service": "test"}, evidence())
            self.assertEqual(len(result), 3)
            self.assertGreaterEqual(result[0].confidence, result[-1].confidence)

    def test_unknown_evidence_citation_is_rejected(self):
        items = self.valid_items()
        items[0]["evidence_ids"] = ["SECRET-LABEL"]
        with patch.dict(os.environ, self.env, clear=True):
            engine = OpenAICompatibleHypothesisEngine(transport=lambda _: response(items))
            with self.assertRaisesRegex(LLMContractError, "unknown"):
                engine.generate({}, evidence())

    def test_out_of_range_confidence_is_rejected(self):
        items = self.valid_items()
        items[0]["confidence"] = 1.5
        with patch.dict(os.environ, self.env, clear=True):
            engine = OpenAICompatibleHypothesisEngine(transport=lambda _: response(items))
            with self.assertRaisesRegex(LLMContractError, "between 0 and 1"):
                engine.generate({}, evidence())

    def test_wrong_hypothesis_count_is_rejected(self):
        with patch.dict(os.environ, self.env, clear=True):
            engine = OpenAICompatibleHypothesisEngine(transport=lambda _: response(self.valid_items()[:2]))
            with self.assertRaisesRegex(LLMContractError, "exactly three"):
                engine.generate({}, evidence())


if __name__ == "__main__":
    unittest.main()

