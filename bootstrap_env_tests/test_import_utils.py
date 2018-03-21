import unittest

from bootstrap_env.utils.import_utils import LazyImportError



class TestImportUtils(unittest.TestCase):
    def test_import_error(self):
        try:
            import DoesNotExists
        except ImportError as err:
            DoesNotExists = LazyImportError(err)

        with self.assertRaises(ImportError) as exception:
            DoesNotExists.foobar

        # TODO: Check exception.args !
