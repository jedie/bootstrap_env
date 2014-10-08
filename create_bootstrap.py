#!/usr/bin/env python

import sys
import virtualenv


code="""
##############################################################

def extend_parser(parser):
    sys.stdout.write("extend_parser called.\\n")

def adjust_options(options, args):
    sys.stdout.write("adjust_options args: %r\\n" % args)

def after_install(options, home_dir):
    sys.stdout.write("after_install from %r\\n" % home_dir)

"""

code += "\n".join([
    "## Generated using: %r v%s" % (virtualenv.__file__, virtualenv.virtualenv_version),
    "## Python v%s" % sys.version.replace("\n", " "),
])

code += """
##############################################################
"""

if __name__ == '__main__':
    out_file="test-bootstrap.py"
    with open(out_file, 'w') as f:
        f.write(virtualenv.create_bootstrap_script(code))

    print("%r written." % out_file)