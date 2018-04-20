
"""
    bootstrap-env PathHelper
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2018 by bootstrap-env team, see AUTHORS for more details.
    :created: 19.04.2018 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)


class PathHelper:
    """
    It's a little bit tricky to get all needed file path.
    So we're boxing all this path stuff here.

    Path in dev.mode, e.g.:

            egg name .......: 'bootstrap_env'
                base dir....: ...env/src/bootstrap-env/bootstrap_env
                 src dir....: ...env/src
                boot file...: ...env/src/bootstrap-env/bootstrap_env/boot_bootstrap_env.py
               admin file...: ...env/src/bootstrap-env/bootstrap_env/bootstrap_env_admin.py
         Requirement file...: ...env/src/bootstrap-env/bootstrap_env/requirements/developer_installation.txt
    Test Requirement file...: ...env/src/bootstrap-env/bootstrap_env/requirements/test_requirements.txt


    Path in package modes are, e.g.:

            egg name .......: 'bootstrap_env'
                base dir....: .../site-packages/bootstrap_env
                 src .......: None
                boot file...: .../site-packages/bootstrap_env/boot_bootstrap_env.py
               admin file...: .../site-packages/bootstrap_env/bootstrap_env_admin.py
         Requirement file...: .../site-packages/bootstrap_env/requirements/normal_installation.txt
    Test Requirement file...: .../site-packages/bootstrap_env/requirements/test_requirements.txt
    """
    DEVELOPER_INSTALL="developer"
    NORMAL_INSTALL="normal"
    REQUIREMENTS = {
        DEVELOPER_INSTALL: "developer_installation.txt",
        NORMAL_INSTALL: "normal_installation.txt",
    }
    TEST_REQUIREMENT = "test_requirements.txt"

    def __init__(self, base_file, boot_filename, admin_filename):
        """
        :param base_file: __file__
        :param boot_filename: e.g.: foobar_boot.py
        :param admin_filename: e.g.: foobar_admin.py
        """
        self.base = Path(base_file).parent
        self.egg_name = self.base.name

        # Construct all needed file path with self.base:

        self.boot_path = Path(self.base, boot_filename)
        self.admin_path = Path(self.base, admin_filename)
        self.req_path = Path(self.base, "requirements")
        self.test_req_path = Path(self.req_path, self.TEST_REQUIREMENT)

        # FIXME: There must exist a better way to detect if the package is
        #        installed as "editable" or a normal package!
        try:
            self.base.relative_to(Path(sys.prefix, "src"))
        except ValueError as err:
            # ValueError: '...env/lib/python3.6/site-packages/foobar' does not start with '...env/src'
            log.debug("%s installed as package (%s)", self.egg_name, err)
            self.install_mode=self.NORMAL_INSTALL
            self.src_path = None
        else:
            log.debug("%s installed as editable", self.egg_name)
            self.install_mode=self.DEVELOPER_INSTALL
            self.src_path = self.base.parent.parent


        self.req_filename = self.REQUIREMENTS[self.install_mode]
        self.req_filepath = Path(self.req_path, self.req_filename)

    @property
    def normal_mode(self):
        return self.install_mode == self.NORMAL_INSTALL

    def assert_all_path(self):
        """
        Check if all path exists. Raise AssertionError if not.
        """
        assert self.boot_path.is_file(), "Boot file not found here: %s" % self.boot_path
        assert self.admin_path.is_file(), "Admin file not found here: %s" % self.admin_path
        assert self.req_path.is_dir(), "Requirements directory not found here: %s" % self.req_path
        assert self.test_req_path.is_file(), "Test requirement not found here: %s" % self.test_req_path

        assert self.req_filepath.is_file(), "Requirement %r not found here: %s" % (self.install_mode, self.req_filepath)

    def print_path(self):
        """
        Just print all paths.
        """
        path_info = [
            ("egg name", self.egg_name),
            ("base", self.base),
            ("src", self.src_path),
            ("boot", self.boot_path),
            ("admin", self.admin_path),
            ("Requirement", self.req_filepath),
            ("Test Requirement", self.test_req_path),
        ]

        width = max([len(info) for info,path in path_info])
        for info, path in path_info:
            if not isinstance(path, Path):
                path_type=""
                path = repr(path)
            else:
                if path.is_file():
                    path_type="file"
                elif path.is_dir():
                    path_type="dir"
                else:
                    path_type="<unknown>"

            print("{info:>{width}} {type:.<7}: {path} ".format(
                width=width,
                info=info,
                path=path,
                type=path_type,
            ))


if __name__ == '__main__':
    import bootstrap_env
    base_file = bootstrap_env.__file__
    # base_file = ".../site-packages/bootstrap_env/__init__.py"

    print("\nbootstrap_env.__file__: %r\n" % base_file)

    path_helper = PathHelper(
        base_file=base_file,
        boot_filename="boot_bootstrap_env.py",
        admin_filename="bootstrap_env_admin.py",
    )
    path_helper.print_path()
    path_helper.assert_all_path()
