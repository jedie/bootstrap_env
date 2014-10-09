#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import hashlib
import os
import sys
import tempfile

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen

try:
    import virtualenv
except ImportError as err:
    print("ERROR: Can't import 'virtualenv', please install it ;)")
    print("More Info:")
    print("    http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation")
    print("(Origin error was: %s)" % err)
    sys.exit(-1)


GET_PIP_URL = "https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py"
GET_PIP_SHA256 = "d43dc33a5670d69dd14a9be1f2b2fa27ebf124ec1b212a47425331040f742a9b"

INSTALL_PIP_FILENAME="bootstrap_install_pip.py"
OUT_FILENAME="bootstrap.py"

HEADER_CODE = '''\
#!/usr/bin/env python

"""
    WARNING: This file is generated with: '{generator}'
    used '{virtualenv_file}' v{virtualenv_version}
    Python v{python_version}
"""

'''.format(
    generator=os.path.basename(__file__),
    virtualenv_file=virtualenv.__file__,
    virtualenv_version=virtualenv.virtualenv_version,
    python_version=sys.version.replace("\n", " ")
)


def surround_code(code, info):
    code = "\n".join([
        "#"*79,
        "## %r START" % info,
        code.strip(),
        "## %r END" % info,
        "#"*79,
    ])
    return "\n\n%s\n\n" % code


def get_install_pip_code(filename):
    with open(filename, "rb") as f:
        content = f.read()

    content = content.decode("UTF-8")

    mark = "# --- CUT here ---"
    start_pos = content.index(mark) + len(mark)
    content = content[start_pos:]

    return surround_code(content, filename)


def get_pip():
    get_pip_temp = os.path.join(tempfile.gettempdir(), "get-pip.py")
    if os.path.isfile(get_pip_temp):
        print("Use %r" % get_pip_temp)
        with open(get_pip_temp, "rb") as f:
            get_pip_content = f.read()
    else:
        print("Request: %r..." % GET_PIP_URL)
        with open(get_pip_temp, "wb") as out_file:
            # Warning: HTTPS requests do not do any verification of the server's certificate.
            f = urlopen(GET_PIP_URL)
            get_pip_content = f.read()
            out_file.write(get_pip_content)

    get_pip_sha = hashlib.sha256(get_pip_content).hexdigest()
    assert get_pip_sha == GET_PIP_SHA256, "Requested get-pip.py sha256 value is wrong! SHA256 is: %r" % get_pip_sha

    get_pip_content = get_pip_content.decode("UTF-8")

    split_index = get_pip_content.index('if __name__ == "__main__":')
    get_pip_content = get_pip_content[:split_index]
    get_pip_content = get_pip_content.replace("def main():", "def get_pip():")

    get_pip_content = "\n".join([line for line in get_pip_content.splitlines() if not line.startswith("#")])

    # print(get_pip_content)
    return surround_code(get_pip_content, "get_pip.py")


def main():
    code = get_install_pip_code(INSTALL_PIP_FILENAME)
    code += get_pip()

    code = virtualenv.create_bootstrap_script(code)

    start_pos = code.index("__version__ = ")
    code = HEADER_CODE + code[start_pos:]

    with open(OUT_FILENAME, 'w') as f:
        f.write(code)

    print("%r written." % OUT_FILENAME)


if __name__ == '__main__':
    main()