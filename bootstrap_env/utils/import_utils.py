

"""
    Utilities
    ~~~~~~~~~

    :created: 21.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""


class LazyImportError:
    """
    Raise a ImportError only if imported object is used.

    usage:

        try:
            import ExternalLib
        except ImportError as err:
            ExternalLib = LazyImportError(err)

    The origin ImportError will re-raise, if you later access to the imported object, e.g.:

        ExternalLib().do_something()

        Traceback (most recent call last):
          File "/foo/bar.py", line 21, in <module>
            import ExternalLib
        ModuleNotFoundError: No module named 'ExternalLib'
    """
    def __init__(self, origin_exception):
        assert isinstance(origin_exception, ImportError)
        self.__origin_exception = origin_exception

    def __getattribute__(self, item):
        if item.endswith("__origin_exception"):
            return super().__getattribute__(item)
        raise ImportError from self.__origin_exception

    def __call__(self, *args, **kwargs):
        raise ImportError from self.__origin_exception


