import unittest
from internal.server.config import CONFIG


class TestConfigClasses(unittest.TestCase):

    def test_config_yaml_connection(self):
        test_config = CONFIG.test

        # --- Assert types ---
        self.assertIsInstance(test_config.mock_boolean, bool)
        self.assertIsInstance(test_config.mock_string, str)
        self.assertIsInstance(test_config.mock_integer, int)
        self.assertIsInstance(test_config.mock_float, float)

        # --- Assert expected values (based on mock YAML) ---
        self.assertTrue(test_config.mock_boolean)
        self.assertEqual(test_config.mock_string, "test_finance.db")
        self.assertEqual(test_config.mock_integer, 42)
        self.assertAlmostEqual(test_config.mock_float, 3.14, places=2)


if __name__ == "__main__":
    unittest.main()
