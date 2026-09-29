import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTests(unittest.TestCase):
    runtime = SimpleNamespace(config={"metadata": {"user_id": "REP-10001"}})

    def test_disqualified_prospect_is_blocked_without_message_id(self):
        result = send_prospect_email.func(
            {"prospect_id": "LEAD-50001", "email": "priya.nair@brightwaveapps.com"},
            "Follow-up",
            "Hello",
            self.runtime,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertNotIn("message_id", result)
        self.assertTrue(result["requires_override"])

    def test_disqualified_prospect_can_be_sent_after_acknowledgement(self):
        result = send_prospect_email.func(
            {"prospect_id": "LEAD-50001", "email": "priya.nair@brightwaveapps.com"},
            "Follow-up",
            "Hello",
            self.runtime,
            acknowledge_disqualified=True,
        )

        self.assertEqual(result["status"], "sent")
        self.assertIn("message_id", result)

    def test_non_disqualified_prospect_is_sent(self):
        result = send_prospect_email.func(
            {"prospect_id": "LEAD-12853", "email": "omar.okafor@lakesideanalytics.com"},
            "Follow-up",
            "Hello",
            self.runtime,
        )

        self.assertEqual(result["status"], "sent")
        self.assertIn("message_id", result)


if __name__ == "__main__":
    unittest.main()
