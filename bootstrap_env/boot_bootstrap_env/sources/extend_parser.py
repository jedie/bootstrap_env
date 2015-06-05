# coding: utf-8

# imports not really needed and just for the editor warning ;)
from bootstrap_env.boot_bootstrap_env.sources.prefix_code import INST_TYPES


def extend_parser(parser):
    # --- CUT here ---
    parser.add_option("--install_type", dest="install_type", choices=INST_TYPES,
        help="Install type: %s (See README!)" % ", ".join(INST_TYPES)
    )