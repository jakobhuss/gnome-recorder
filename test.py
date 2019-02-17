#!/usr/bin/python3
import sys
import unittest
from io import StringIO

import record


class Testing(unittest.TestCase):

    def test_audio_device(self):
        self.assertGreaterEqual(len(record.audio_devices()), 1)

    def test_overwrite_false(self):
        sys.stdin = StringIO('n')
        with self.assertRaises(SystemExit):
            record.check_overwrite_file('test.py')

    def test_overwrite_false_with_NO(self):
        sys.stdin = StringIO('No')
        with self.assertRaises(SystemExit):
            record.check_overwrite_file('test.py')

    def test_overwrite_true(self):
        sys.stdin = StringIO('y')
        record.check_overwrite_file('test.py')
        self.assertTrue(True)
