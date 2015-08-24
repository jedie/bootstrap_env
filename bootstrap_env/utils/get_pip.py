# coding: utf-8

"""
    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

import hashlib
import os
import tempfile
import sys

PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

from bootstrap_env.utils.sourcecode_utils import surround_code


# Alternative url is: https://bootstrap.pypa.io/get-pip.py
MASTER_GET_PIP_URL = "https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py"

# 'get-pip.py' v7.1.2
HASH_GET_PIP_URL = "https://raw.githubusercontent.com/pypa/pip/3dfa1f9a55d25587e9e97a27d8c87943e4b6aa54/contrib/get-pip.py"
GET_PIP_SHA256 = "d1f66b3848abc6fd1aeda3bb7461101f6a909c3b08efa3ecc1f561712269469c"

# Only for info message:
HISTORY_PAGE = "https://github.com/pypa/pip/commits/develop/contrib/get-pip.py"


def get_pip_tempfile():
    return os.path.join(tempfile.gettempdir(), "get-pip.py")

def get_pip():
    """
    Request 'get_pip.py' from given url and return the modified content.
    The Requested content will be cached into the default temp directory.
    """
    get_pip_temp = get_pip_tempfile()
    if os.path.isfile(get_pip_temp):
        print("Use %r" % get_pip_temp)
        with open(get_pip_temp, "rb") as f:
            get_pip_content = f.read()
    else:
        print("Request: %r..." % HASH_GET_PIP_URL)
        with open(get_pip_temp, "wb") as out_file:
            # Warning: HTTPS requests do not do any verification of the server's certificate.
            f = urlopen(HASH_GET_PIP_URL)
            get_pip_content = f.read()
            out_file.write(get_pip_content)

        # FIXME: How to easier check if there is a newer 'get-pip.py' version was commited???
        # see also: http://www.python-forum.de/viewtopic.php?f=1&t=35572 (de)
        print("Request: %r..." % MASTER_GET_PIP_URL)
        f = urlopen(MASTER_GET_PIP_URL)
        master_content = f.read()
        if get_pip_content != master_content:
            print("WARNING: 'get-pip.py' master changed! Maybe a new version was commited?")
            print("Please check:")
            print("\t%s" % HISTORY_PAGE)
            print("And report here:")
            print("\thttps://github.com/jedie/bootstrap_env/issues")
        else:
            print("Requested content of 'get-pip.py' is up-to-date, ok.")

    # Check SHA256 hash:
    get_pip_sha = hashlib.sha256(get_pip_content).hexdigest()
    assert get_pip_sha == GET_PIP_SHA256, "Requested get-pip.py sha256 value is wrong! SHA256 is: %r (Maybe it was commit a new version?!?)" % get_pip_sha
    print("get-pip.py SHA256: %r, ok." % get_pip_sha)

    get_pip_content = get_pip_content.decode("UTF-8")

    # Cut the "start" code:
    split_index = get_pip_content.index('if __name__ == "__main__":')
    get_pip_content = get_pip_content[:split_index]

    # Rename main() to get_pip():
    get_pip_content = get_pip_content.replace("def main():", "def get_pip():")

    # TODO: Remove comment lines
    # Important: Since the usage of b85 encoding the '#' character will not be masked!

    # print(get_pip_content)
    get_pip_content = surround_code(get_pip_content, "get_pip.py")
    get_pip_content = "\n\n%s\n\n" % get_pip_content
    return get_pip_content

