# AI-TTRPG/rules_engine/tests/test_data.py

import unittest
from unittest.mock import patch
import os
import json

# Import the data_loader module and the loader function
from rules_engine import data_loader

class TestDataLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure data is loaded once for the entire test class."""
        data_loader.load_data()

    def test_stats_and_skills_loaded(self):
        """Test that stats and skills data is loaded correctly."""
        self.assertTrue(data_loader.STATS_LIST, "STATS_LIST should not be empty")
        self.assertIsInstance(data_loader.STATS_LIST, list, "STATS_LIST should be a list")
        self.assertIn("Might", data_loader.STATS_LIST, "Core stat 'Might' should be in STATS_LIST")

        self.assertTrue(data_loader.ALL_SKILLS, "ALL_SKILLS should not be empty")
        self.assertIsInstance(data_loader.ALL_SKILLS, dict, "ALL_SKILLS should be a dictionary")
        self.assertIn("Athletics", data_loader.ALL_SKILLS, "Sample skill 'Athletics' should be in ALL_SKILLS")
        self.assertEqual(data_loader.ALL_SKILLS["Athletics"]["stat"], "Reflexes", "Athletics governing stat should be 'Reflexes'")

    def test_abilities_loaded(self):
        """Test that ability data is loaded into a dictionary."""
        self.assertTrue(data_loader.ABILITY_DATA, "ABILITY_DATA should not be empty")
        self.assertIsInstance(data_loader.ABILITY_DATA, dict, "ABILITY_DATA should be a dictionary")
        self.assertIn("Force", data_loader.ABILITY_DATA, "Ability school 'Force' should be a key in ABILITY_DATA")
        self.assertEqual(data_loader.ABILITY_DATA["Force"]["resource"], "Presence", "'Force' resource should be 'Presence'")

    def test_talents_loaded_and_corrected(self):
        """Test that talent data is loaded and stat names are corrected."""
        self.assertTrue(data_loader.TALENT_DATA, "TALENT_DATA should not be empty")
        self.assertIsInstance(data_loader.TALENT_DATA, dict, "TALENT_DATA should be a dictionary")
        self.assertIn("single_stat_mastery", data_loader.TALENT_DATA, "'single_stat_mastery' should be a key in TALENT_DATA")

        # Check for 'Vitality' correction
        found_vitality_talent = False
        for talent in data_loader.TALENT_DATA.get("single_stat_mastery", []):
            if talent.get("stat") == "Vitality" and talent.get("talent_name") == "Resist Toxin":
                found_vitality_talent = True
                break
        self.assertTrue(found_vitality_talent, "Failed to find a talent corrected from 'Constitution' to 'Vitality'")

    def test_kingdom_features_loaded_and_corrected(self):
        """Test that kingdom features are processed into a flat map and corrected."""
        self.assertTrue(data_loader.FEATURE_STATS_MAP, "FEATURE_STATS_MAP should not be empty")
        self.assertIsInstance(data_loader.FEATURE_STATS_MAP, dict, "FEATURE_STATS_MAP should be a dictionary")
        self.assertIn("Predator's Gaze", data_loader.FEATURE_STATS_MAP, "Feature 'Predator''s Gaze' should be in the map")

        # Check for 'Vitality' correction in a specific feature's mods
        predator_gaze_mods = data_loader.FEATURE_STATS_MAP["Predator's Gaze"].get("mods", {})
        self.assertIn("Vitality", predator_gaze_mods.get("-1", []), "Predator's Gaze mods should contain 'Vitality' instead of 'Constitution'")

    def test_deeply_nested_ability_description(self):
        """Check for a specific, deeply nested ability description to ensure data integrity."""
        force_school = data_loader.ABILITY_DATA.get("Force", {})
        self.assertIn("branches", force_school)

        control_branch = next((branch for branch in force_school["branches"] if branch["branch"] == "Control (External Movement)"), None)
        self.assertIsNotNone(control_branch, "Control branch not found in Force school")

        tier_1 = next((tier for tier in control_branch["tiers"] if tier["tier"] == "T1"), None)
        self.assertIsNotNone(tier_1, "T1 not found in Control branch")

        self.assertEqual(tier_1["description"], "Minor Shove: Push 1 target 1m. (Contested Might check).", "Deeply nested description for Minor Shove is incorrect.")

if __name__ == '__main__':
    unittest.main()
