#!/usr/bin/python3
import unittest

import record


class Testing(unittest.TestCase):

    def test_audio_device(self):
        self.assertGreaterEqual(len(record.audio_devices()), 1)
