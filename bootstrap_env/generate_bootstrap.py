# coding: utf-8

"""
    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import os
import sys



try:
    import virtualenv
except ImportError as err:
    print("ERROR: Can't import 'virtualenv', please install it ;)")
    print("More Info:")
    print("    http://virtualenv.readthedocs.org/en/latest/virtualenv.html#installation")
    print("(Origin error was: %s)" % err)
    sys.exit(-1)

from bootstrap_env.utils.get_pip import get_pip
from bootstrap_env.utils.sourcecode_utils import cut_path, surround_code, get_code, abs_py_path
from bootstrap_env import __version__ as bootstrap_env_version
from bootstrap_env.utils import bootstrap_install_pip

INSTALL_PIP_FILENAME = abs_py_path(bootstrap_install_pip) # bootstrap_install_pip.py
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
    virtualenv_file=cut_path(virtualenv.__file__),
    virtualenv_version=virtualenv.virtualenv_version,
    python_version=sys.version.replace("\n", " ")
)


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
        add_extend_parser=None, add_adjust_options=None, add_after_install=None,
        cut_mark="# --- CUT here ---", prefix=None, suffix=None):
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
    out_filename = os.path.normpath(os.path.abspath(out_filename))

    print("\nGenerate bootstrap file: %r...\n" % out_filename)

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

    start_pos = code.index("import ")
    code = HEADER_CODE + code[start_pos:]

    for func_name in ("get_pip", "extend_parser", "adjust_options", "after_install"):
        func_def = "def %s(" % func_name
        if not func_def in code:
            raise AssertionError("Function %r missing in generated code!" % func_name)

    with open(out_filename, 'w') as f:
        f.write(code)

    print("\n%r written.\n" % out_filename)
