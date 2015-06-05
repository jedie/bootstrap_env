#!/usr/bin/env python
# coding: utf-8

import os

from bootstrap_env.generate_bootstrap import generate_bootstrap


EXAMPLE_PATH=os.path.abspath(os.path.dirname(__file__))


if __name__ == '__main__':
    generate_bootstrap(
        out_filename=os.path.join(EXAMPLE_PATH, "..", "..", "boot_example_env.py"),
        add_extend_parser=os.path.join(EXAMPLE_PATH, "extend_parser.py"),
        add_adjust_options=os.path.join(EXAMPLE_PATH, "adjust_options.py"),
        add_after_install=os.path.join(EXAMPLE_PATH, "after_install.py"),
        cut_mark="# --- CUT here ---",
        prefix=None, # Optional code that will be inserted before extend_parser() code part.
        suffix=None, # Optional code that will be inserted after after_install() code part.
    )