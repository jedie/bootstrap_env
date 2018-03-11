"""
    Base Admin
    ~~~~~~~~~~

    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""


import os  # isort:skip

assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"  # isort:skip

import logging
import re
import subprocess
import sys
from pathlib import Path

from pkg_resources import safe_name

from bootstrap_env.boot_bootstrap_env import (PACKAGE_NAME, ROOT_PATH, Cmd2,
                                              VerboseSubprocess, __version__,
                                              in_virtualenv)

log = logging.getLogger(__name__)


SELF_FILE_PATH=Path(__file__).resolve()                               # .../src/pylucid/pylucid/pylucid_admin.py
OWN_FILE_NAME=SELF_FILE_PATH.name                                      # pylucid_admin.py

# print("PACKAGE_NAME: %s" % PACKAGE_NAME)
# print("ROOT_PATH: %s" % ROOT_PATH)

# print("SELF_FILE_PATH: %s" % SELF_FILE_PATH)
# print("OWN_FILE_NAME: %s" % OWN_FILE_NAME)


class Requirements:
    DEVELOPER_INSTALL="developer"
    NORMAL_INSTALL="normal"
    REQUIREMENTS = {
        DEVELOPER_INSTALL: "developer_installation.txt",
        NORMAL_INSTALL: "normal_installation.txt",
    }
    def __init__(self):
        self.src_path = Path(sys.prefix, "src")

        # pip install -e will change the package name via pkg_resources.safe_name
        # e.g.: "foo_bar" -> "foo-bar"
        package_dir_name = safe_name(PACKAGE_NAME)

        src_bootstrap_env_path = Path(self.src_path, package_dir_name)

        if src_bootstrap_env_path.is_dir():
            print("bootstrap_env is installed as editable here: %s" % src_bootstrap_env_path)
            self.install_mode=self.DEVELOPER_INSTALL
        else:
            print("bootstrap_env is installed as packages here: %s" % ROOT_PATH)
            self.install_mode=self.NORMAL_INSTALL

    @property
    def normal_mode(self):
        return self.install_mode == self.NORMAL_INSTALL

    def get_requirement_path(self):
        """
        :return: Path(.../bootstrap_env/requirements/)
        """
        requirement_path = Path(ROOT_PATH, PACKAGE_NAME, "requirements").resolve()
        if not requirement_path.is_dir():
            raise RuntimeError("Requirements directory not found here: %s" % requirement_path)
        return requirement_path

    def get_requirement_file_path(self):
        """
        :return: Path(.../bootstrap_env/requirements/<mode>_installation.txt)
        """
        requirement_path = self.get_requirement_path()
        filename = self.REQUIREMENTS[self.install_mode]

        requirement_file_path = Path(requirement_path, filename).resolve()
        if not requirement_file_path.is_file():
            raise RuntimeError("Requirements file not found here: %s" % requirement_file_path)

        return requirement_file_path





class AdminShell(Cmd2):
    OWN_FILE_NAME = OWN_FILE_NAME
    version = __version__

    #_________________________________________________________________________
    # Normal user commands:

    def do_pytest(self, arg):
        """
        Run tests via pytest
        """
        try:
            import pytest
        except ImportError as err:
            print("ERROR: Can't import pytest: %s (pytest not installed, in normal installation!)" % err)
        else:
            root_path = str(ROOT_PATH)
            print("chdir %r" % root_path)
            os.chdir(root_path)

            args = sys.argv[2:]
            print("Call Pytest with args: %s" % repr(args))
            exit_code = pytest.main(args=args)
            sys.exit(exit_code)

    def do_pip_freeze(self, arg):
        """
        Just run 'pip freeze'
        """
        return_code = VerboseSubprocess("pip3", "freeze").verbose_call(check=False)

    def do_update_env(self, arg):
        """
        Update all packages in virtualenv.

        (Call this command only in a activated virtualenv.)
        """
        if not in_virtualenv():
            self.stdout.write("\nERROR: Only allowed in activated virtualenv!\n\n")
            return

        pip3_path = Path(sys.prefix, "bin", "pip3")
        if not pip3_path.is_file():
            print("ERROR: pip not found here: '%s'" % pip3_path)
            return

        print("pip found here: '%s'" % pip3_path)
        pip3_path = str(pip3_path)

        return_code = VerboseSubprocess(
            pip3_path, "install", "--upgrade", "pip"
        ).verbose_call(check=False)

        req = Requirements()

        # Update the requirements files by...
        if req.normal_mode:
            # ... update 'bootstrap_env' PyPi package
            return_code = VerboseSubprocess(
                pip3_path, "install", "--upgrade", PACKAGE_NAME
            ).verbose_call(check=False)
        else:
            # ... git pull bootstrap_env sources
            return_code = VerboseSubprocess(
                "git", "pull", "origin",
                cwd=ROOT_PATH
            ).verbose_call(check=False)

            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=ROOT_PATH
            ).verbose_call(check=False)

        requirement_file_path = str(req.get_requirement_file_path())

        # Update with requirements files:
        self.stdout.write("Use: '%s'\n" % requirement_file_path)
        return_code = VerboseSubprocess(
            "pip3", "install",
            "--exists-action", "b", # action when a path already exists: (b)ackup
            "--upgrade",
            "--requirement", requirement_file_path,
            timeout=120  # extended timeout for slow Travis ;)
        ).verbose_call(check=False)

        if not req.normal_mode:
            # Run pip-sync only in developer mode
            return_code = VerboseSubprocess(
                "pip-sync", requirement_file_path,
                cwd=ROOT_PATH
            ).verbose_call(check=False)

            # 'reinstall' bootstrap_env editable, because it's not in 'requirement_file_path':
            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=ROOT_PATH
            ).verbose_call(check=False)

        self.stdout.write("Please restart %s\n" % self.own_filename)
        sys.exit(0)

    #_________________________________________________________________________
    # Developer commands:

    def do_upgrade_requirements(self, arg):
        """
        1. Convert via 'pip-compile' *.in requirements files to *.txt
        2. Append 'piprot' informations to *.txt requirements.
        """
        req = Requirements()
        requirements_path = req.get_requirement_path()

        for requirement_in in requirements_path.glob("*.in"):
            requirement_in = Path(requirement_in).name

            if requirement_in.startswith("basic_"):
                continue

            requirement_out = requirement_in.replace(".in", ".txt")

            self.stdout.write("_"*79 + "\n")

            # We run pip-compile in ./requirements/ and add only the filenames as arguments
            # So pip-compile add no path to comments ;)

            return_code = VerboseSubprocess(
                "pip-compile", "--verbose", "--upgrade", "-o", requirement_out, requirement_in,
                cwd=requirements_path
            ).verbose_call(check=True)

            if not requirement_in.startswith("test_"):
                req_out = Path(requirements_path, requirement_out)
                with req_out.open("r") as f:
                    requirement_out_content = f.read()

            self.stdout.write("_"*79 + "\n")
            output = [
                "\n#\n# list of out of date packages made with piprot:\n#\n"
            ]

            s = VerboseSubprocess("piprot", "--outdated", requirement_out, cwd=requirements_path)
            for line in s.iter_output(check=True):
                print(line, flush=True)
                output.append("# %s" % line)

            self.stdout.write("\nUpdate file %r\n" % requirement_out)
            filepath = Path(requirements_path, requirement_out).resolve()
            assert filepath.is_file(), "File not exists: %r" % filepath
            with open(filepath, "a") as f:
                f.writelines(output)

    def do_change_editable_address(self, arg):
        """
        Replace git remote url from github read-only 'https' to 'git@'
        e.g.:

        OLD: https://github.com/<user>/<project>.git
        NEW: git@github.com:<user>/<project>.git

        **This is only developer with github write access ;)**

        executes e.g.:

        git remote set-url origin git@github.com:<user>/<project>.git
        """
        req = Requirements()
        if req.normal_mode:
            print("ERROR: Only available in 'developer' mode!")
            return

        src_path = req.src_path  # Path instance pointed to 'src' directory
        for p in src_path.iterdir():
            if not p.is_dir():
                continue

            if str(p).endswith(".bak"):
                continue

            print("\n")
            print("*"*79)
            print("Change: %s..." % p)

            try:
                output = VerboseSubprocess(
                    "git", "remote", "-v",
                    cwd=str(p),
                ).verbose_output(check=False)
            except subprocess.CalledProcessError:
                print("Skip.")
                continue

            (name, url) = re.findall("(\w+?)\s+([^\s]*?)\s+", output)[0]
            print("Change %r url: %r" % (name, url))

            new_url=url.replace("https://github.com/", "git@github.com:")
            if new_url == url:
                print("ERROR: url not changed!")
                continue

            VerboseSubprocess("git", "remote", "set-url", name, new_url, cwd=str(p)).verbose_call(check=False)
            VerboseSubprocess("git", "remote", "-v", cwd=str(p)).verbose_call(check=False)


def main():
    AdminShell().cmdloop()


if __name__ == '__main__':
    main()
