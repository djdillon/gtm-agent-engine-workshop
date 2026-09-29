import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class ProspectUpdateTests(unittest.TestCase):
    def test_update_persists_technology_and_refreshes_profile(self):
        prospect_id = "LEAD-12853"
        technology = "Test Technology"
        record = data_service.get_prospect_record(prospect_id)
        original_tech_stack = list(record["tech_stack"])

        try:
            data_service.invalidate_profile(prospect_id)
            initial_profile = build_prospect_profile.invoke({"prospect_id": prospect_id})
            self.assertNotIn(technology, initial_profile["prospect_profile"]["tech_stack"])

            result = data_service.update_prospect_info(prospect_id, technology)

            self.assertTrue(result["updated"])
            self.assertIn(technology, data_service.fetch_tech_stack(prospect_id))
            updated_profile = build_prospect_profile.invoke({"prospect_id": prospect_id})
            self.assertIn(technology, updated_profile["prospect_profile"]["tech_stack"])
        finally:
            record["tech_stack"] = original_tech_stack
            data_service.invalidate_profile(prospect_id)


if __name__ == "__main__":
    unittest.main()
