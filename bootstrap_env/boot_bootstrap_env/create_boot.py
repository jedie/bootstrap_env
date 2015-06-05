#!/usr/bin/env python
# coding: utf-8

import os

import bootstrap_env
from bootstrap_env import generate_bootstrap
from bootstrap_env.boot_bootstrap_env import sources
from bootstrap_env.utils.pip_utils import requirements_definitions
from bootstrap_env.utils.sourcecode_utils import abs_package_path, get_code


REQ_FILENAMES=(
    "normal_installation.txt",
    "git_readonly_installation.txt",
    "developer_installation.txt",
)


BASE_PATH=abs_package_path(bootstrap_env) # create absolute path from __file__ attribute
SOURCES_PATH=abs_package_path(sources)

PREFIX_SCRIPT=os.path.join(SOURCES_PATH, "prefix_code.py")

REQ_BASE_PATH=os.path.join(BASE_PATH, "requirements")
print("requirement files path: %r" % REQ_BASE_PATH)

BOOT_FILEPATH=os.path.join(BASE_PATH, "boot.py")


def generate():
    assert os.path.isdir(REQ_BASE_PATH)

    prefix_code = "\n".join([
        requirements_definitions(REQ_BASE_PATH, REQ_FILENAMES),
        get_code(PREFIX_SCRIPT, generate_bootstrap.INSTALL_PIP_MARK),
    ])

    generate_bootstrap.generate_bootstrap(
        out_filename=BOOT_FILEPATH,
        add_extend_parser=os.path.join(SOURCES_PATH, "extend_parser.py"),
        add_adjust_options=os.path.join(SOURCES_PATH, "adjust_options.py"),
        add_after_install=os.path.join(SOURCES_PATH, "after_install.py"),
        cut_mark="# --- CUT here ---",
        prefix=prefix_code, # Optional code that will be inserted before extend_parser() code part.
        suffix=None, # Optional code that will be inserted after after_install() code part.
    )



if __name__ == '__main__':
    generate()