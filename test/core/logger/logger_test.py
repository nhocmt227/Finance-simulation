import unittest
from internal.core.logger import logger


class TestLogger(unittest.TestCase):
    def test_logger_instance(self):
        self.assertIsNotNone(logger)
        self.assertTrue(logger.hasHandlers())
        logger.info("Logger test passed.")


if __name__ == "__main__":
    unittest.main()
