import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import gtm_agent


class ProspectToolSanitizationTest(unittest.TestCase):
    def assert_safe(self, result):
        self.assertNotIn("billing_qualification", str(result))
        for field in ("tax_id", "date_of_birth", "card_on_file", "credit_check_ref"):
            self.assertNotIn(field, str(result))

    def test_prospect_tools_exclude_billing_fields(self):
        record = {
            "name": "Sven Smith",
            "email": "sven.smith@example.com",
            "annual_revenue": 70000000,
            "disqualified": False,
            "enrichment_source": "ZoomInfo",
            "billing_qualification": {
                "tax_id": "318-52-7761",
                "date_of_birth": "1979-11-02",
                "card_on_file": "4716220984513307",
                "credit_check_ref": "EXPN-71852",
            },
            "engagement_history": [],
            "account_details": [],
            "tech_stack": ["Snowflake"],
        }
        with (
            patch.object(gtm_agent.data_service, "get_prospect_record", return_value=record),
            patch.object(gtm_agent.data_service, "fetch_engagement_history", return_value=[]),
            patch.object(gtm_agent.data_service, "fetch_account_details", return_value=[]),
            patch.object(gtm_agent.data_service, "fetch_tech_stack", return_value=["Snowflake"]),
            patch.object(gtm_agent.data_service, "get_profile_from_db", return_value={"prospect_profile": None}),
        ):
            prospect = gtm_agent.get_prospect.invoke("LEAD-18993")
            profile = gtm_agent.build_prospect_profile.invoke("LEAD-18993")

        for result in (prospect, profile):
            self.assert_safe(result)

        cached = {"prospect_id": "LEAD-18993", **record}
        with (
            patch.object(gtm_agent.data_service, "get_profile_from_db", return_value={"prospect_profile": cached}),
            patch.object(gtm_agent.data_service, "save_profile_to_db") as save_profile,
        ):
            cached_result = gtm_agent.build_prospect_profile.invoke("LEAD-18993")

        self.assert_safe(cached_result)
        self.assert_safe(save_profile.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
