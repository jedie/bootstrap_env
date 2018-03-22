#!/usr/bin/python3

"""
    Base Admin
    ~~~~~~~~~~

    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""


import logging
import os
from pathlib import Path

# Bootstrap-Env
import bootstrap_env
from bootstrap_env.admin_shell.normal_shell import AdminShell
from bootstrap_env.admin_shell.requirements import Requirements

log = logging.getLogger(__name__)

SELF_FILE_PATH=Path(__file__).resolve()                         # /src/bootstrap-env/bin/bootstrap_env_admin.py
PACKAGE_PATH=Path(bootstrap_env.__file__).parent                # /src/bootstrap-env/bootstrap_env/
PACKAGE_NAME=PACKAGE_PATH.name                                  # bootstrap_env
REQUIREMENT_PATH=Path(PACKAGE_PATH, "requirements")             # /src/bootstrap-env/bootstrap_env/requirements/
OWN_FILE_NAME=SELF_FILE_PATH.name                               # bootstrap_env_admin.py

print("SELF_FILE_PATH: %s" % SELF_FILE_PATH)
print("PACKAGE_NAME: %s" % PACKAGE_NAME)
print("REQUIREMENT_PATH: %s" % REQUIREMENT_PATH)
print("OWN_FILE_NAME: %s" % OWN_FILE_NAME)


def main():
    assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"
    requirements = Requirements(
        requirement_path=REQUIREMENT_PATH,
        package_name=PACKAGE_NAME,
    )
    if requirements.normal_mode:
        # Installed in "normal" mode (as Package from PyPi)
        ShellClass = AdminShell
    else:
        # Installed in "developer" mode (as editable from source)
        # Import here, because developer_shell imports packages that
        # only installed in "developer" mode ;)
        from bootstrap_env.admin_shell.developer_shell import DeveloperAdminShell
        ShellClass = DeveloperAdminShell

    ShellClass(
        package_path=PACKAGE_PATH,
        package_name=PACKAGE_NAME,
        requirements=requirements,
        self_filename=OWN_FILE_NAME,
    ).cmdloop()


if __name__ == '__main__':
    main()
