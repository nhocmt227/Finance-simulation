import unittest
from internal.core.logger import LOGGER


class TestLogger(unittest.TestCase):
    def test_logger_instance(self):
        self.assertIsNotNone(LOGGER)
        self.assertTrue(LOGGER.hasHandlers())
        LOGGER.info("Logger test passed.")


if __name__ == "__main__":
    unittest.main()
