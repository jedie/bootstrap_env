#!/usr/bin/python3

"""
    Bootstrap
    ~~~~~~~~~

    A interactive shell for booting the 'bootstrap_env' project.

    Note:
        - This file is "self contained".
        - It used **only** stuff from Python lib.
        - So it's "run able" on a bare python 3 installation
        - On debian / ubuntu the 'python3-venv' package is needed!

    usage, e.g.:

        $ wget https://raw.githubusercontent.com/jedie/bootstrap_env/bootstrap_env_v3/bootstrap_env/boot_bootstrap_env.py
        $ python3 boot_bootstrap_env.py

        boot_bootstrap_env.py> boot ~/bootstrap_env_env

    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""
import re
import sys  # isort:skip

import time

if sys.version_info < (3, 5):  # isort:skip
    print("\nERROR: Python 3.5 or greater is required!")
    print("(Current Python Verison is %s)\n" % sys.version.split(" ",1)[0])
    sys.exit(101)

import cmd
import logging
import os
import subprocess
import traceback
from pathlib import Path

try:
    import venv
except ImportError as err:
    # e.g.: debian / ubuntu doesn't have venv installed, isn't it?!?
    print("\nERROR: 'venv' not available: %s (Maybe 'python3-venv' package not installed?!?)" % err)

try:
    import ensurepip
except ImportError as err:
    # e.g.: debian / ubuntu doesn't have venv installed, isn't it?!?
    print("\nERROR: 'ensurepip' not available: %s (Maybe 'python3-venv' package not installed?!?)" % err)


__version__ = "0.1.0"


log = logging.getLogger(__name__)


PACKAGE_NAME="bootstrap_env" # PyPi package name

# admin shell console script entry point name ('setup.py
# (used to call 'upgrade_requirements' after virtualenv creation)
# It's the 'scripts' keyword argument in project 'setup.py'
# see:
# https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-scripts-keyword-argument
#
ADMIN_FILE_NAME="bootstrap_env_admin.py" # File under .../<project>/foobar_admin.py

# Note:
#   on 'master' branch: '--pre' flag must not be set: So the last release on PyPi will be installed.
#   on 'develop' branch: set the '--pre' flag and publish 'preview' versions on PyPi.
#
DEVELOPER_INSTALL=["-e", "git+https://github.com/jedie/bootstrap_env.git@master#egg=%s" % PACKAGE_NAME]
NORMAL_INSTALL=[
    "--pre", # https://pip.pypa.io/en/stable/reference/pip_install/#pre-release-versions
    PACKAGE_NAME
]

SELF_FILE_PATH=Path(__file__).resolve()               # .../src/bootstrap-env/bootstrap_env/boot_bootstrap_env.py
ROOT_PATH=Path(SELF_FILE_PATH, "..", "..").resolve()  # .../src/bootstrap_env/
OWN_FILE_NAME=SELF_FILE_PATH.name                     # boot_bootstrap_env.py

print("SELF_FILE_PATH: %s" % SELF_FILE_PATH)
print("ROOT_PATH: %s" % ROOT_PATH)
print("OWN_FILE_NAME: %s" % OWN_FILE_NAME)


def in_virtualenv():
    # Maybe this is not the best way?!?
    return "VIRTUAL_ENV" in os.environ


if in_virtualenv():
    print("Activated virtualenv detected: %r (%s)" % (sys.prefix, sys.executable))
else:
    print("We are not in a virtualenv, ok.")


SUBPROCESS_TIMEOUT=60  # default timeout for subprocess calls



class Colorizer:
    """
    Borrowed from Django:
    https://github.com/django/django/blob/master/django/utils/termcolors.py

    >>> c = Colorizer()
    >>> c.supports_colors()
    True
    >>> c.color_support = True
    >>> c.colorize('no color')
    'no color'
    >>> c.colorize('bold', opts=("bold",))
    '\\x1b[1mbold\\x1b[0m'
    >>> c.colorize("colors!", foreground="red", background="blue", opts=("bold", "blink"))
    '\\x1b[31;44;1;5mcolors!\\x1b[0m'
    """
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self._stdout = stdout
        self._stderr = stderr

        color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')

        self._foreground_colors = dict([(color_names[x], '3%s' % x) for x in range(8)])
        self._background_colors = dict([(color_names[x], '4%s' % x) for x in range(8)])
        self._opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

        self.color_support = self._supports_colors()

    def _supports_colors(self):
        if sys.platform in ('win32', 'Pocket PC'):
            return False

        # isatty is not always implemented!
        if hasattr(self._stdout, 'isatty') and self._stdout.isatty():
            return True
        else:
            return False

    def colorize(self, text, foreground=None, background=None, opts=()):
        """
        Returns your text, enclosed in ANSI graphics codes.
        """
        if not self.color_support:
            return text

        code_list = []

        if foreground:
            code_list.append(self._foreground_colors[foreground])
        if background:
            code_list.append(self._background_colors[background])

        for option in opts:
            code_list.append(self._opt_dict[option])

        if not code_list:
            return text

        return "\x1b[%sm%s\x1b[0m" % (';'.join(code_list), text)

    def _out_err(self, func, *args, flush=False, **kwargs):
        text = self.colorize(*args, **kwargs)
        func.write("%s\n" % text)
        if flush:
            func.flush()

    def out(self, *args, flush=False, **kwargs):
        """ colorize and print to stdout """
        self._out_err(self._stdout, *args, flush=flush, **kwargs)

    def err(self, *args, flush=False, **kwargs):
        """ colorize and print to stderr """
        self._out_err(self._stderr, *args, flush=flush, **kwargs)

    def demo(self):
        for background_color in sorted(self._background_colors.keys()):
            line = ["%10s:" % background_color]
            for foreground_color in sorted(self._foreground_colors.keys()):
                line.append(
                    self.colorize("  %s  " % foreground_color,
                        foreground=foreground_color, background=background_color
                    )
                )

            for opt in sorted(self._opt_dict.keys()):
                line.append(
                    self.colorize("  %s  " % opt,
                        background=background_color, opts=(opt,)
                    )
                )

            self.out("".join(line), background=background_color)


colorizer = Colorizer()
# colorizer.demo()



class VerboseSubprocess:
    """
    Verbose Subprocess
    """
    def __init__(self, *popenargs, env_updates=None, timeout=SUBPROCESS_TIMEOUT, universal_newlines=True, stderr=subprocess.STDOUT, **kwargs):
        """
        :param popenargs: 'args' for subprocess.Popen()
        :param env_updates: dict to overwrite os.environ.
        :param timeout: pass to subprocess.Popen()
        :param kwargs: pass to subprocess.Popen()
        """
        self.popenargs = popenargs
        self.kwargs = kwargs

        self.kwargs["timeout"] = timeout
        self.kwargs["universal_newlines"] = universal_newlines
        self.kwargs["stderr"] = stderr

        self.args_str = " ".join([str(x) for x in self.popenargs])

        env = self.kwargs.get("env", os.environ.copy())
        env["PYTHONUNBUFFERED"]="1" # If a python script called ;)
        env["bufsize"] = 1

        self.env_updates = env_updates
        if self.env_updates is not None:
            env.update(env_updates)

        self.kwargs["env"] = env

    def print_call_info(self):
        print("")
        print("_"*79)

        kwargs_txt=[]
        for key, value in self.kwargs.items():
            if key == "env":
                continue
            key = colorizer.colorize(key, foreground="magenta", opts=("bold",))
            value = colorizer.colorize(value, foreground="green", opts=("bold",))
            kwargs_txt.append("%s=%s" % (key, value))

        txt = "Call: '{args}' with: {kwargs}".format(
            args=colorizer.colorize(self.args_str, foreground="cyan", opts=("bold",)),
            kwargs=", ".join(kwargs_txt)
        )

        if self.env_updates is not None:
            txt += colorizer.colorize(" env:", foreground="magenta", opts=("bold",))
            txt += colorizer.colorize(repr(self.env_updates), opts=("bold",))

        print(txt)
        print("", flush=True)

    def print_exit_code(self, exit_code):
        txt = "\nExit code %r from %r\n" % (exit_code, self.args_str)
        if exit_code:
            colorizer.err(txt, foreground="red", flush=True)
        else:
            colorizer.out(txt, foreground="green", flush=True)

    def verbose_call(self, check=True):
        """
        run subprocess.call()

        :param check: if True and subprocess exit_code !=0: sys.exit(exit_code) after run.
        :return: process exit code
        """
        self.print_call_info()

        try:
            exit_code = subprocess.call(self.popenargs, **self.kwargs)
        except KeyboardInterrupt:
            print("\nExit %r\n" % self.args_str, flush=True)
            exit_code=None # good idea?!?

        sys.stderr.flush()

        self.print_exit_code(exit_code)
        if check and exit_code:
            sys.exit(exit_code)

        return exit_code

    def verbose_output(self, check=True):
        """
        run subprocess.check_output()

        :param check: if True and subprocess exit_code !=0: sys.exit(exit_code) after run.
        :return: process output
        """
        self.print_call_info()

        try:
            return subprocess.check_output(self.popenargs, **self.kwargs)
        except subprocess.CalledProcessError as err:
            print("\n%s" % err)
            if check:
                sys.exit(err.returncode)
            raise

    def iter_output(self, check=True):
        """
        A subprocess with tee ;)
        """
        self.print_call_info()

        orig_timeout = self.kwargs.pop("timeout")

        self.kwargs.update({
            "stdout":subprocess.PIPE,
            "stderr":subprocess.STDOUT,
        })

        proc=subprocess.Popen(self.popenargs, **self.kwargs)

        end_time = time.time() + orig_timeout
        for line in iter(proc.stdout.readline, ''):
            yield line

            if time.time()>end_time:
                raise subprocess.TimeoutExpired(self.popenargs, orig_timeout)

        if check and proc.returncode:
            sys.exit(proc.returncode)

    def print_output(self, check=True):
        for line in self.iter_output(check=check):
            print(line, flush=True)




def display_errors(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            return "%s: %s" % (err.__class__.__name__, err)

    return wrapped


class Cmd2(cmd.Cmd):
    """
    Enhanced version of 'Cmd' class:
        - command alias
        - methods can be called directly from commandline: e.g.: ./foobar.py --help
        - Display
    """
    own_filename = SELF_FILE_PATH.name  # Path(__file__).name ;)
    version = __version__

    command_alias = { # used in self.precmd()
        "q": "quit", "EOF": "quit", "exit": "quit",
        "": "help", # Just hit ENTER -> help
        "--help": "help", "-h": "help", "-?": "help",
    }

    unknown_command="*** Unknown command: %r ***\n"

    # Will be append to 'doc_leader' in self.do_help():
    complete_hint="\nUse <{key}> to command completion.\n"
    missing_complete="\n(Sorry, no command completion available.)\n" # if 'readline' not available

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        intro_line = '{filename} shell v{version}'.format(
            filename=self.own_filename,
            version=self.version
        )
        intro_line = colorizer.colorize(intro_line, foreground="blue", background="black", opts=("bold",))

        self.intro = (
            '\n{intro_line}\n'
            'Type help or ? to list commands.\n'
        ).format(intro_line=intro_line)

        self.prompt = colorizer.colorize(self.own_filename, foreground="cyan")
        self.prompt += colorizer.colorize("> ", opts=("bold",))

        self.doc_header = "Available commands (type help <topic>):\n"
        self.doc_leader = (
            "\nHint: All commands can be called directly from commandline.\n"
            "e.g.: $ ./{filename} help\n"
        ).format(
            filename=self.own_filename,
        )

        # e.g.: $ bootstrap_env_admin.py boot /tmp/bootstrap_env-env -> run self.do_boot("/tmp/bootstrap_env-env") on startup
        args = sys.argv[1:]
        if args:
            self.cmdqueue = [" ".join(args)]

    def default(self, line):
        """ Called on an input line when the command prefix is not recognized. """
        colorizer.err(self.unknown_command % line, foreground="red")

    @display_errors
    def _complete_list(self, items, text, line, begidx, endidx):
        if text:
            return [x for x in items if x.startswith(text)]
        else:
            return items

    @display_errors
    def _complete_path(self, text, line, begidx, endidx):
        """
        complete a command argument with a existing path

        usage e.g.:
            class FooCmd(Cmd2):
                def complete_foobar(self, text, line, begidx, endidx):
                    return self._complete_path(text, line, begidx, endidx)

                def do_foobar(self, path): # 'path' is type string!
                    print("path:", path)
        """
        try:
            destination = line.split(" ", 1)[1]
        except IndexError:
            destination = "."

        if destination=="~":
            return [os.sep]

        destination = Path(destination).expanduser().resolve()

        if not destination.is_dir():
            destination = destination.parent.resolve()

        if destination.is_dir():
            complete_list = [x.stem + os.sep for x in destination.iterdir() if x.is_dir()]
            if text:
                if text in complete_list:
                    return [text + os.sep]

                complete_list = [x for x in complete_list if x.startswith(text)]
        else:
            complete_list = []

        return complete_list

    def get_doc_line(self, command):
        """
        return the first line of the DocString.
        If no DocString: return None
        """
        assert command.startswith("do_")
        doc=getattr(self, command, None).__doc__
        if doc is not None:
            doc = doc.strip().split("\n",1)[0]
        return doc

    _complete_hint_added=False
    def do_help(self, arg):
        """
        List available commands with "help" or detailed help with "help cmd".
        """
        if arg:
            # Help for one command
            return super().do_help(arg)

        # List available commands:

        self.stdout.write("%s\n" % self.doc_leader)
        self.stdout.write("%s\n" % self.doc_header)

        commands = [name for name in self.get_names() if name.startswith("do_")]
        commands.sort()
        max_length = max([len(name) for name in commands])

        for command in commands:
            doc_line = self.get_doc_line(command) or "(Undocumented command)"

            command = command[3:] # remove "do_"

            command = "{cmd:{width}}".format(cmd=command, width=max_length)
            command = colorizer.colorize(command, opts=("bold",))

            self.stdout.write(" {cmd} - {doc}\n".format(
                cmd=command,
                doc=doc_line
            ))

        self.stdout.write("\n")

    def do_quit(self, arg):
        "Exit this interactiv shell"
        print("\n\nbye")
        return True

    def precmd(self, line):
        """
        1. Apply alias list
        2. print first DocString line (if exists), before start the command
        """
        try:
            line=self.command_alias[line]
        except KeyError:
            pass

        cmd = line.split(" ",1)[0]
        doc_line = self.get_doc_line("do_%s" % cmd)
        if doc_line:
            colorizer.out("\n\n *** %s ***\n" % doc_line, background="cyan", opts=("bold",))

        return line

    def postcmd(self, stop, line):
        # stop if we are called with commandline arguments
        if len(sys.argv)>1:
            stop = True
        return stop


class bootstrap_envEnvBuilder(venv.EnvBuilder):
    verbose = True

    def __init__(self, requirements):
        super().__init__(with_pip=True)
        self.requirements = requirements

    def ensure_directories(self, env_dir):
        print(" * Create the directories for the environment.")
        return super().ensure_directories(env_dir)

    def create_configuration(self, context):
        print(" * Create 'pyvenv.cfg' configuration file.")
        return super().create_configuration(context)

    def setup_python(self, context):
        print(" * Set up a Python executable in the environment.")
        return super().setup_python(context)

    def _setup_pip(self, context):
        print(" * Installs or upgrades pip in a virtual environment.")
        return super()._setup_pip(context)

    def setup_scripts(self, context):
        print(" * Set up scripts into the created environment.")
        return super().setup_scripts(context)

    def post_setup(self, context):
        """
        Set up any packages which need to be pre-installed into the
        virtual environment being created.

        :param context: The information for the virtual environment
                        creation request being processed.
        """
        print(" * post-setup modification")

        def call_new_python(*args, **kwargs):
            """
            Do the same as bin/activate so that <args> runs in a "activated" virtualenv.
            """
            kwargs.update({
                "env_updates": {
                    "VIRTUAL_ENV": context.env_dir,
                    "PATH": "%s:%s" % (context.bin_path, os.environ["PATH"]),
                }
            })
            VerboseSubprocess(*args, **kwargs).verbose_call(
                check=True # sys.exit(return_code) if return_code != 0
            )

        call_new_python("pip", "install", "--upgrade", "pip")

        # Install bootstrap_env
        #   in normal mode as package from PyPi
        #   in dev. mode as editable from github
        call_new_python(
            "pip", "install",
            # "--verbose",
            *self.requirements
        )

        # Check if ".../bin/bootstrap_env_admin.py" exists
        bootstrap_env_admin_path = Path(context.bin_path, ADMIN_FILE_NAME)
        if not bootstrap_env_admin_path.is_file():
            print("ERROR: admin script not found here: '%s'" % bootstrap_env_admin_path)
            VerboseSubprocess("ls", "-la", str(context.bin_path)).verbose_call()
            sys.exit(-1)

        # Install all requirements
        call_new_python(ADMIN_FILE_NAME, "update_env", timeout=240)  # extended timeout for slow Travis ;)


class BootBootstrapEnvShell(Cmd2):
    def _resolve_path(self, path):
        return Path(path).expanduser().resolve()

    def complete_boot(self, text, line, begidx, endidx):
        # print("text: %r" % text)
        # print("line: %r" % line)
        return self._complete_path(text, line, begidx, endidx)

    def _parse_requirements(self, requirement_string):
        requirements = []
        for line in requirement_string.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):

                line = line.split("# ", 1)[0] # Remove pip-compile comments e.g.: "... # via foo"
                line = line.rstrip()

                if line.startswith("-e"): # split editables
                    requirements += line.split(" ")
                else:
                    requirements.append(line)
        return requirements

    def _boot(self, destination, requirements):
        """
        Create a bootstrap_env virtualenv and install requirements.
        """
        destination = Path(destination).expanduser()
        if destination.exists():
            self.stdout.write("\nERROR: Path '%s' already exists!\n" % destination)
            sys.exit(1)

        self.stdout.write("Create virtualenv: '%s'...\n\n" % destination)

        builder = bootstrap_envEnvBuilder(requirements)
        builder.create(str(destination))

        self.stdout.write("\n")

        if not destination.is_dir():
            self.stdout.write("ERROR: Creating virtualenv!\n")
            sys.exit(1)
        else:
            self.stdout.write("virtualenv created at: '%s'\n" % destination)

    def do_boot(self, destination):
        """
        Bootstrap bootstrap_env virtualenv in "normal" mode.

        usage:
            > boot [path]

        Create a bootstrap_env virtualenv in the given [path].
        Install packages via PyPi and read-only sources from github.

        The destination path must not exist yet!

        (used the requirements/normal_installation.txt)
        """
        self._boot(destination, requirements=NORMAL_INSTALL)
    complete_boot = complete_boot

    def do_boot_developer(self, destination):
        """
        Bootstrap bootstrap_env virtualenv in "developer" mode.
        All own projects installed as editables via github HTTPS (readonly)

        **Should be only used for developing/contributing. All others: Use normal 'boot' ;) **

        usage:
            > boot_developer [path]

        Create a bootstrap_env virtualenv in the given [path].
        Install packages via PyPi and read-only sources from github.

        The destination path must not exist yet!

        (used the requirements/developer_installation.txt)
        """
        self._boot(destination, requirements=DEVELOPER_INSTALL)
    complete_boot_developer = complete_boot


def main():
    BootBootstrapEnvShell().cmdloop()


if __name__ == '__main__':
    main()