import os
import unittest
from internal.core.bugger import bugger
from internal.server.config import CONFIG


class TestBuggerLogger(unittest.TestCase):

    def setUp(self):
        self.log_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../../logs", CONFIG.core.bugger.filename
            )
        )
        # Clear the log file before test
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_log_string_message(self):
        try:
            bugger.log("This is a test error string.")
        except Exception as e:
            self.fail(f"BUGGER.log raised an exception with string input: {e}")

    def test_log_dict_message(self):
        try:
            bugger.log({"error": "test_error", "message": "Testing dict logging."})
        except Exception as e:
            self.fail(f"BUGGER.log raised an exception with dict input: {e}")

    def test_log_file_created(self):
        bugger.log("Checking file creation.")
        self.assertTrue(
            os.path.exists(self.log_file), "Bugger log file was not created."
        )

    def test_log_file_content(self):
        bugger.log("Test content in bugger log.")
        with open(self.log_file, "r") as f:
            content = f.read()
        self.assertIn("Test content in bugger log", content)


if __name__ == "__main__":
    unittest.main()
