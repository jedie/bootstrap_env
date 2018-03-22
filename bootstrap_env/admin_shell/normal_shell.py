
"""
    Admin Shell commands available in 'normal' install mode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    IMPORTANT:
        Every import from external packages must be made with LazyImportError!
        Otherwise the bootstrap will fail, because no external package is
        available in bootstrap process!

    :created: 03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

import os
import sys
from pathlib import Path

# Bootstrap-Env
from bootstrap_env.boot_bootstrap_env import Cmd2, VerboseSubprocess, __version__, get_pip_file_name, in_virtualenv
from bootstrap_env.utils.import_utils import LazyImportError
from bootstrap_env.version import __version__ as bootstrap_env_version

# External libs:
try:
    from cookiecutter.main import cookiecutter
except ImportError as err:
    # Re-Raise ImportError on first usage
    cookiecutter = LazyImportError(err)



class AdminShell(Cmd2):
    """
    Normal user commands.
    Only this commands are available in 'normal' installation mode.
    """
    version = __version__

    def __init__(self, package_path, package_name, requirements, *args, **kwargs):
        self.package_path = package_path # /src/bootstrap-env/bootstrap_env/
        self.package_name = package_name # bootstrap_env
        self.requirements = requirements # bootstrap_env.admin_shell.requirements.Requirements instance

        super().__init__(*args, **kwargs)

    def do_pytest(self, arg=None):
        """
        Run tests via pytest
        """
        try:
            import pytest
        except ImportError as err:
            print("ERROR: Can't import pytest: %s (pytest not installed, in normal installation!)" % err)
        else:
            root_path = str(self.package_path.parent)
            print("chdir %r" % root_path)
            os.chdir(root_path)

            args = sys.argv[2:]
            print("Call Pytest with args: %s" % repr(args))
            exit_code = pytest.main(args=args)
            sys.exit(exit_code)

    def do_pip_freeze(self, arg=None):
        """
        Just run 'pip freeze'
        """
        return_code = VerboseSubprocess("pip3", "freeze").verbose_call(check=False)

    def do_update_env(self, arg=None):
        """
        Update all packages in virtualenv.

        (Call this command only in a activated virtualenv.)
        """
        if not in_virtualenv():
            self.stdout.write("\nERROR: Only allowed in activated virtualenv!\n\n")
            return

        if sys.platform == 'win32':
            bin_dir_name="Scripts"
        else:
            bin_dir_name = "bin"

        pip3_path = Path(sys.prefix, bin_dir_name, get_pip_file_name()) # e.g.: .../bin/pip3
        if not pip3_path.is_file():
            print("ERROR: pip not found here: '%s'" % pip3_path)
            return

        print("pip found here: '%s'" % pip3_path)
        pip3_path = str(pip3_path)

        # Upgrade pip first:
        if sys.platform == 'win32':
            # Note: On windows it will crash with a PermissionError: [WinError 32]
            # because pip can't replace himself while running ;)
            # Work-a-round is "python -m pip install --upgrade pip"
            # see also: https://github.com/pypa/pip/issues/3804
            return_code = VerboseSubprocess(
                sys.executable or "python",
                "-m", "pip", "install", "--upgrade", "pip",
            ).verbose_call(check=False)
        else:
            return_code = VerboseSubprocess(
                pip3_path, "install", "--upgrade", "pip"
            ).verbose_call(check=False)

        root_path = self.package_path.parent

        # Update the requirements files by...
        if self.requirements.normal_mode:
            # ... update 'bootstrap_env' PyPi package
            return_code = VerboseSubprocess(
                pip3_path, "install", "--upgrade", self.package_name
            ).verbose_call(check=False)
        else:
            # ... git pull bootstrap_env sources
            return_code = VerboseSubprocess(
                "git", "pull", "origin",
                cwd=str(root_path)
            ).verbose_call(check=False)

            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=str(root_path)
            ).verbose_call(check=False)

        requirement_file_path = str(self.requirements.get_requirement_file_path())

        # Update with requirements files:
        self.stdout.write("Use: '%s'\n" % requirement_file_path)
        return_code = VerboseSubprocess(
            pip3_path, "install",
            "--exists-action", "b", # action when a path already exists: (b)ackup
            "--upgrade",
            "--requirement", requirement_file_path,
            timeout=120  # extended timeout for slow Travis ;)
        ).verbose_call(check=False)

        self.stdout.write("Please restart %s\n" % self.self_filename)
        sys.exit(0)

    def do_pip_sync(self, arg=None):
        """
        run pip-sync (use with care)

        pip-sync will install/upgrade/uninstall everything necessary to match the requirements.txt contents.

        Be careful: pip-sync is meant to be used only with a requirements.txt generated by pip-compile!
        """
        if self.package_name == "bootstrap_env":
            print("ERROR: command not allowed for 'bootstrap_env' !\n")
            print(
                "bootstrap_env doesn't use pip-compile,"
                " because Bootstrap-env should be used as a tool in other projects"
                " and the projects himself should pin requirements ;) "
            )
            return

        # Run pip-sync only in developer mode
        return_code = VerboseSubprocess(
            "pip-sync", str(self.requirements.requirement_path),
            cwd=str(self.package_path.parent)
        ).verbose_call(check=False)

        self.stdout.write("Please restart %s\n" % self.self_filename)
        sys.exit(0)

    def complete_generate_bootstrap(self, text, line, begidx, endidx):
        # print("text: %r" % text)
        # print("line: %r" % line)
        return self._complete_path(text, line, begidx, endidx)

    def confirm(self, txt, confirm_values=("y", "j")):
        if input("\n%s" % txt).lower() in confirm_values:
            return True
        return False

    def do_generate_bootstrap(self, arg=None):
        """
        Generate new bootstrap file via cookiecutter

        direct call, e.g.:

        bootstrap_env_admin.py generate_bootstrap ~/new_project
        """
        if not arg:
            print("INFO: No output path given.")

        output_dir = Path(arg).expanduser().resolve()

        if output_dir.is_dir():
            print("Create bootstrap file in: %s" % output_dir)
            print("ERROR: output path already exists!")
            return

        txt = "Create bootstrap file in: %s ? [Y/N]" % output_dir
        if not self.confirm(txt):
            print("Abort.")
            return

        repro_path = Path(self.package_path, "boot_source")
        result = cookiecutter(
            template=str(repro_path),
            output_dir=str(output_dir),
            extra_context={
                "_version": bootstrap_env_version,
            }
        )
        print("bootstrap file created here: %s" % result)
