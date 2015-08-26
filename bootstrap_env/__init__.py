# coding: utf-8

"""
    bootstrap-env
    ~~~~~~~~~~~~~

    :copyleft: 2015 by bootstrap-env team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

import warnings


__version__="0.5.4"


# Old API e.g.: bootstrap_env.create_bootstrap.generate_bootstrap()
# New API e.g.: bootstrap_env.generate_bootstrap.generate_bootstrap()

from bootstrap_env import generate_bootstrap as _new_api


class OldApi(object):
    def __getattr__(self, name):
        new_api = getattr(_new_api, name)
        warnings.warn(
            "You use the old bootstrap_env API! This will be removed in the future!",
            FutureWarning,
            stacklevel=2
        )
        return new_api


create_bootstrap = OldApi()