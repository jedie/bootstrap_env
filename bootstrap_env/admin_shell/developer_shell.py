import re
import subprocess
from pathlib import Path

from cookiecutter.main import cookiecutter
from packaging.version import parse

# Bootstrap-Env
from bootstrap_env.admin_shell.normal_shell import AdminShell
from bootstrap_env.admin_shell.requirements import Requirements
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess
from bootstrap_env.version import __version__ as bootstrap_env_version


class DeveloperAdminShell(AdminShell):
    """
    Developer commands
    ~~~~~~~~~~~~~~~~~~

    Expand AdminShell with some "developer" commands.
    This is only useable in "developer" mode (Installed as editable from source).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.requirements.normal_mode:
            raise RuntimeError("ERROR: Only available in 'developer' mode!")

    def do_upgrade_requirements(self, arg):
        """
        1. Convert via 'pip-compile' *.in requirements files to *.txt
        2. Append 'piprot' informations to *.txt requirements.
        """
        requirements_path = self.requirements.get_requirement_path()

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
        src_path = self.requirements.src_path  # Path instance pointed to 'src' directory
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

    def do_generate_boot_file(self, arg):
        """
        Generate bootstrap file via cookiecutter
        """
        # https://packaging.pypa.io/en/latest/version/
        parsed_bootstrap_env_version = parse(bootstrap_env_version)

        if parsed_bootstrap_env_version.is_prerelease:
            release_type = "pre-release and development version"
        else:
            release_type = "PyPi stable"

        repro_path = Path(self.package_path, "boot_source")

        result = cookiecutter(
            template=str(repro_path),
            no_input=True,
            overwrite_if_exists=True,
            output_dir=str(self.package_path.parent),
            extra_context={
                "version": bootstrap_env_version,
                "package_name": "bootstrap_env",
                "release_type": release_type,
            }
        )
        print("bootstrap file created here: %s" % result)
