#!/usr/bin/env python
# coding: utf-8

import os
from bootstrap_env.create_bootstrap import generate_bootstrap

if __name__ == '__main__':
    generate_bootstrap(
        out_filename="boot_example.py",
        add_extend_parser=os.path.join("example", "extend_parser.py"),
        add_adjust_options=os.path.join("example", "adjust_options.py"),
        add_after_install=os.path.join("example", "after_install.py"),
        cut_mark="# --- CUT here ---",
        prefix=None, # Optional code that will be inserted before extend_parser() code part.
        suffix=None, # Optional code that will be inserted after after_install() code part.
    )