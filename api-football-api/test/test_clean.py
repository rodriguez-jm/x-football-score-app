import unittest
import os
import logging

from clean import *

class TestClean(unittest.TestCase):

    def test_log_file_exists(self):
        self.assertTrue(os.path.exists(log_file))

    def test_completed_file_deleted(self):
        if os.path.exists(completed_file):
            os.remove(completed_file)
        self.assertFalse(os.path.exists(completed_file))

    def test_logging_info(self):
        logger = logging.getLogger()
        handlers = logger.handlers
        self.assertEqual(len(handlers), 1)
        handler = handlers[0]
        self.assertIsInstance(handler, logging.FileHandler)
        self.assertEqual(handler.level, logging.INFO)
        self.assertEqual(handler.filename, log_file)
        self.assertEqual(handler.formatter._fmt, "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)s)")

if __name__ == '__main__':
    unittest.main()