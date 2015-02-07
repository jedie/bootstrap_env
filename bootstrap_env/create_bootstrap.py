# coding: utf-8

"""
    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import hashlib
import os
import sys
import tempfile

PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

try:
    import virtualenv
except ImportError as err:
    print("ERROR: Can't import 'virtualenv', please install it ;)")
    print("More Info:")
    print("    http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation")
    print("(Origin error was: %s)" % err)
    sys.exit(-1)

from bootstrap_env import __version__ as bootstrap_env_version


# Alternative url is: https://bootstrap.pypa.io/get-pip.py
MASTER_GET_PIP_URL = "https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py"

# 'get-pip.py' v6.0.8
HASH_GET_PIP_URL = "https://raw.githubusercontent.com/pypa/pip/b9f2d5d5bb4c9dba8dbba3cc09a24fefb12fb38e/contrib/get-pip.py"
GET_PIP_SHA256 = "8a02784f08572986d6d4538d5b4fa68030cf459df42b497382a4a5caac135e07"

# Only for info message:
HISTORY_PAGE = "https://github.com/pypa/pip/commits/develop/contrib/get-pip.py"

INSTALL_PIP_FILENAME = os.path.join(os.path.abspath(os.path.dirname(__file__)), "bootstrap_install_pip.py")
INSTALL_PIP_MARK = "# --- CUT here ---"

HEADER_CODE = '''\
#!/usr/bin/env python

"""
    WARNING: This file is generated with: bootstrap_env v{bootstrap_env_version}
    https://pypi.python.org/pypi/bootstrap_env/
    script file: '{generator}'
    used '{virtualenv_file}' v{virtualenv_version}
    Python v{python_version}
"""

'''.format(
    bootstrap_env_version=bootstrap_env_version,
    generator=os.path.basename(__file__),
    virtualenv_file=virtualenv.__file__,
    virtualenv_version=virtualenv.virtualenv_version,
    python_version=sys.version.replace("\n", " ")
)


def surround_code(code, info, indent=""):
    """
    Mark the beginning and end of the code.
    So, it's easier to find it in the generated bootstrap file ;)
    """
    comment_line = "#" * 79
    return "\n".join([
        "%s%s" % (indent, comment_line),
        "%s## %r START" % (indent, info),
        code.strip("\n"),
        "%s## %r END" % (indent, info),
        "%s%s" % (indent, comment_line),
        "", # add a new line at the end
    ])


def get_code(filename, cut_mark, indent=""):
    """
    Read a UTF-8 file and return the content after cut_mark, surrounded with comments.
    """
    print("Reade code from: %r..." % filename)
    with open(filename, "rb") as f:
        content = f.read()

    content = content.decode("UTF-8")

    start_pos = content.index(cut_mark) + len(cut_mark)
    content = content[start_pos:]

    return surround_code(content, filename, indent)


def get_pip():
    """
    Request 'get_pip.py' from given url and return the modified content.
    The Requested content will be cached into the default temp directory.
    """
    get_pip_temp = os.path.join(tempfile.gettempdir(), "get-pip.py")
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


def merge_code(extend_parser_code, adjust_options_code, after_install_code):
    """
    merge the INSTALL_PIP_FILENAME code with the given code parts.
    """
    install_pip_code = get_code(INSTALL_PIP_FILENAME, INSTALL_PIP_MARK)

    code = ""
    in_extend_parser = False
    in_adjust_options = False
    in_after_install = False
    for line in install_pip_code.splitlines(True): # with keepends:
        if line.startswith("def "):
            if in_extend_parser == True: # leave extend_parser():
                code += extend_parser_code + "\n\n"
                in_extend_parser = False
            elif in_adjust_options == True: # leave adjust_options():
                code += adjust_options_code + "\n\n"
                in_adjust_options = False
            elif in_after_install == True: # leave after_install():
                code += after_install_code + "\n\n"
                in_after_install = False

            if line.startswith("def extend_parser("):
                in_extend_parser = True
            elif line.startswith("def adjust_options("):
                in_adjust_options = True
            elif line.startswith("def after_install("):
                in_after_install = True

        code += line

    # FIXME: Add code block if no def function exist
    #        after extend_parser(), adjust_options() and after_install() !
    if in_extend_parser == True: # leave extend_parser():
        code += extend_parser_code + "\n\n"
    elif in_adjust_options == True: # leave adjust_options():
        code += adjust_options_code + "\n\n"
    elif in_after_install == True: # leave after_install():
        code += after_install_code + "\n\n"

    return code


def generate_bootstrap(out_filename,
        add_extend_parser, add_adjust_options, add_after_install,
        cut_mark, prefix=None, suffix=None):
    """
    Generate the bootstrap:
     - download "get-pip.py"
     - read all source files
     - all virtualenv.create_bootstrap_script()
     - merge everything together

    :param out_filename: Filepath for the generated bootstrap file

    :param add_extend_parser: source file for extend_parser() additional
    :param add_adjust_options: source file for adjust_options() additional
    :param add_after_install: source file for after_install() additional

    :param cut_mark: mark for start cutting the used code

    :param prefix: Optional code that will be inserted before extend_parser() code part.
    :param suffix: Optional code that will be inserted after after_install() code part.
    """
    print("Generate bootstrap file: %r..." % out_filename)

    if prefix:
        print("Add prefix code.")
        code = surround_code(prefix, "prefix code")
    else:
        code = ""

    extend_parser_code = get_code(add_extend_parser, cut_mark, indent="    ")
    adjust_options_code = get_code(add_adjust_options, cut_mark, indent="    ")
    after_install_code = get_code(add_after_install, cut_mark, indent="    ")

    code += merge_code(extend_parser_code, adjust_options_code, after_install_code)

    if suffix:
        print("Add suffix code.")
        code += surround_code(suffix, "suffix code")

    code += get_pip()

    code = virtualenv.create_bootstrap_script(code)

    start_pos = code.index("__version__ = ")
    code = HEADER_CODE + code[start_pos:]

    for func_name in ("get_pip", "extend_parser", "adjust_options", "after_install"):
        func_def = "def %s(" % func_name
        if not func_def in code:
            raise AssertionError("Function %r missing in generated code!" % func_name)

    with open(out_filename, 'w') as f:
        f.write(code)

    print("%r written." % out_filename)
