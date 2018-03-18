from pathlib import Path

from cookiecutter.main import cookiecutter
from pip._vendor.packaging.version import parse as parse_version

# Bootstrap-Env
from bootstrap_env.version import __version__ as bootstrap_env_version


CWD = Path().cwd()
SELF_FILE_PATH=Path(__file__).resolve()                # .../src/bootstrap-env/bootstrap_env/generate_boot.py
REPRO_PATH=Path(SELF_FILE_PATH.parent, "boot_source")  # .../src/bootstrap_env/bootstrap_env/boot_source/
OUTPUT_PATH=Path(SELF_FILE_PATH.parent, "..")          # .../src/bootstrap-env/

REPRO_PATH = REPRO_PATH.relative_to(CWD)
OUTPUT_PATH = OUTPUT_PATH.relative_to(CWD)


if __name__ == '__main__':
    print("SELF_FILE_PATH: %s" % SELF_FILE_PATH)
    print("REPRO_PATH: %s" % REPRO_PATH)
    print("OUTPUT_PATH: %s" % OUTPUT_PATH)

    parsed_bootstrap_env_version = parse_version(bootstrap_env_version)

    if parsed_bootstrap_env_version.is_prerelease:
        release_type = "pre-release and development version"
    else:
        release_type = "PyPi stable"

    cookiecutter(
        template=str(REPRO_PATH),
        no_input=True,
        overwrite_if_exists=True,
        output_dir=str(OUTPUT_PATH),
        extra_context={
            "version": bootstrap_env_version,
            "package_name": "bootstrap_env",
            "release_type": release_type,
        }
    )
