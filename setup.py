#!/usr/bin/env python3
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2019 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function

import distutils
import os
import shutil
import subprocess
import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 5):  # isort:skip
    print("\nERROR: Python 3.5 or greater is required!")
    print("(Current Python Verison is %s)\n" % sys.version.split(" ", 1)[0])
    sys.exit(101)




PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

__version__ = "<unknown>"


def read(*args):
    return open(os.path.join(PACKAGE_ROOT, *args)).read()


exec(read("bootstrap_env", "version.py"))


class BaseCommand(distutils.cmd.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class TestCommand(BaseCommand):
    """Distutils command to run tests via py.test: 'python setup.py test'."""

    description = "Run tests via 'py.test'."

    def run(self):
        self.announce("Running tests...", level=distutils.log.INFO)
        returncode = subprocess.call(["pytest"])
        sys.exit(returncode)


def get_authors():
    try:
        with open(os.path.join(PACKAGE_ROOT, "AUTHORS"), "r") as f:
            authors = [l.strip(" *\r\n") for l in f if l.strip().startswith("*")]
    except Exception as err:
        authors = "[Error: %s]" % err
    return authors


# _____________________________________________________________________________
# convert creole to ReSt on-the-fly, see also:
# https://github.com/jedie/python-creole/wiki/Use-In-Setup
long_description = None
for arg in ("test", "check", "register", "sdist", "--long-description"):
    if arg in sys.argv:
        try:
            from creole.setup_utils import get_long_description
        except ImportError as err:
            raise ImportError("%s - Please install python-creole - e.g.: pip install python-creole" % err)
        else:
            long_description = get_long_description(PACKAGE_ROOT)
        break
# ----------------------------------------------------------------------------


if "publish" in sys.argv:
    """
    'publish' helper for setup.py

    Build and upload to PyPi, if...
        ... __version__ doesn't contains "dev"
        ... we are on git 'master' branch
        ... git repository is 'clean' (no changed files)

    Upload with "twine", git tag the current version and git push --tag

    The cli arguments will be pass to 'twine'. So this is possible:
     * Display 'twine' help page...: ./setup.py publish --help
     * use testpypi................: ./setup.py publish --repository=test

    TODO: Look at: https://github.com/zestsoftware/zest.releaser

    Source: https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/setup_publish.py
    copyleft 2015-2019 Jens Diemer - GNU GPL v2+
    """
    assert sys.version_info[0] > 2, "Python v3 is needed!"

    import_error = False
    try:
        # Test if wheel is installed, otherwise the user will only see:
        #   error: invalid command 'bdist_wheel'
        import wheel
    except ImportError as err:
        print("\nError: %s" % err)
        print("\nMaybe https://pypi.org/project/wheel is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install wheel")
        import_error = True

    try:
        import twine
    except ImportError as err:
        print("\nError: %s" % err)
        print("\nMaybe https://pypi.org/project/twine is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install twine")
        import_error = True

    if import_error:
        sys.exit(-1)

    def verbose_check_output(*args):
        """ 'verbose' version of subprocess.check_output() """
        call_info = "Call: %r" % " ".join(args)
        try:
            output = subprocess.check_output(args, universal_newlines=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            print("\n***ERROR:")
            print(err.output)
            raise
        return call_info, output

    def verbose_check_call(*args):
        """ 'verbose' version of subprocess.check_call() """
        print("\tCall: %r\n" % " ".join(args))
        subprocess.check_call(args, universal_newlines=True)

    def confirm(txt):
        print("\n%s" % txt)
        if input("\nPublish anyhow? (Y/N)").lower() not in ("y", "j"):
            print("Bye.")
            sys.exit(-1)

    for key in ("dev", "rc"):
        if key in __version__:
            confirm("WARNING: Version contains %r: v%s\n" % (key, __version__))
            break

    print("\nCheck if we are on 'master' branch:")
    call_info, output = verbose_check_output("git", "branch", "--no-color")
    print("\t%s" % call_info)
    if "* master" in output:
        print("OK")
    else:
        confirm("\nNOTE: It seems you are not on 'master':\n%s" % output)

    ##########################################################################
    # bootstrap_env check if boot file is up-to-date
    # Just update own boot file and the "prero is clean" check will faile, on changes ;)
    #
    verbose_check_call("bootstrap_env_admin.py", "update_own_boot_file")
    #
    ##########################################################################

    print("\ncheck if if git repro is clean:")
    call_info, output = verbose_check_output("git", "status", "--porcelain")
    print("\t%s" % call_info)
    if output == "":
        print("OK")
    else:
        print("\n *** ERROR: git repro not clean:")
        print(output)
        sys.exit(-1)

    print("\nRun './setup.py check':")
    call_info, output = verbose_check_output("./setup.py", "check")
    if "warning" in output:
        print(output)
        confirm("Warning found!")
    else:
        print("OK")

    print("\ncheck if pull is needed")
    verbose_check_call("git", "fetch", "--all")
    call_info, output = verbose_check_output("git", "log", "HEAD..origin/master", "--oneline")
    print("\t%s" % call_info)
    if output == "":
        print("OK")
    else:
        print("\n *** ERROR: git repro is not up-to-date:")
        print(output)
        sys.exit(-1)
    verbose_check_call("git", "push")

    print("\nCleanup old builds:")

    def rmtree(path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            print("\tremove tree:", path)
            shutil.rmtree(path)

    rmtree("./dist")
    rmtree("./build")

    print("\nbuild but don't upload...")
    log_filename = "build.log"
    with open(log_filename, "a") as log:
        call_info, output = verbose_check_output(
            sys.executable or "python", "setup.py", "sdist", "bdist_wheel", "bdist_egg"
        )
        print("\t%s" % call_info)
        log.write(call_info)
        log.write(output)
    print("Build output is in log file: %r" % log_filename)

    git_tag = "v%s" % __version__

    print("\ncheck git tag")
    call_info, output = verbose_check_output("git", "log", "HEAD..origin/master", "--oneline")
    if git_tag in output:
        print("\n *** ERROR: git tag %r already exists!" % git_tag)
        print(output)
        sys.exit(-1)
    else:
        print("OK")

    print("\nUpload with twine:")
    twine_args = sys.argv[1:]
    twine_args.remove("publish")
    twine_args.insert(1, "dist/*")
    print("\ttwine upload command args: %r" % " ".join(twine_args))
    from twine.commands.upload import main as twine_upload

    twine_upload(twine_args)

    print("\ngit tag version")
    verbose_check_call("git", "tag", git_tag)

    print("\ngit push tag to server")
    verbose_check_call("git", "push", "--tags")

    sys.exit(0)


setup(
    name="bootstrap_env",
    version=__version__,
    py_modules=["bootstrap_env"],
    provides=["bootstrap_env"],
    description="Create a complete self contained virtualenv bootstrap file",
    long_description=long_description,
    author=get_authors(),
    author_email="bootstrap_env@jensdiemer.de",
    maintainer="Jens Diemer",
    maintainer_email="bootstrap_env@jensdiemer.de",
    url="https://github.com/jedie/bootstrap_env",
    python_requires=">=3.5",
    install_requires=(
        # same as bootstrap_env/requirements/basic_requirements.txt
        "cookiecutter",
        "packaging",
    ),
    packages=find_packages(),
    include_package_data=True,  # include package data under version control
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-scripts-keyword-argument
    scripts=["bootstrap_env/boot_bootstrap_env.py", "bootstrap_env/bootstrap_env_admin.py"],
    #
    # We don"t set "install_requires", because the requirements.txt files should be used!
    # Bootstrap works in this way:
    #   - create virtualenv
    #   - pip install <project>
    #   - <project>_admin update_env
    #
    zip_safe=False,
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={"test": TestCommand},
)
