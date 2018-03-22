import unittest
from pathlib import Path

import bootstrap_env


class BootstrapEnvTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_path = Path(bootstrap_env.__file__).resolve().parent

    def test_setup(self):
        self.assertTrue(self.base_path.is_dir())
