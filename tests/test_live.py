import unittest

from incidentlens.live import LiveTelemetryClient


class LiveClientTests(unittest.TestCase):
    def test_capture_uses_three_read_only_backend_requests(self):
        requests = []

        def transport(request):
            requests.append(request)
            return {"ok": True, "url": request.full_url}

        client = LiveTelemetryClient(transport=transport)
        result = client.capture("checkout", "up", 10, 20)
        self.assertEqual(len(requests), 3)
        self.assertEqual(requests[0].get_method(), "GET")
        self.assertEqual(requests[1].get_method(), "POST")
        self.assertEqual(requests[2].get_method(), "GET")
        self.assertTrue(result["read_only"])
        self.assertEqual(result["telemetry_mode"], "live_local_capture")

    def test_capture_scopes_service_in_log_and_trace_requests(self):
        requests = []

        def transport(request):
            requests.append(request)
            return {}

        LiveTelemetryClient(transport=transport).capture("email", "up", 10, 20)
        self.assertIn(b'"service.name": "email"', requests[1].data)
        self.assertIn("service=email", requests[2].full_url)


if __name__ == "__main__":
    unittest.main()
