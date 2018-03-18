import sys
from pathlib import Path

from pkg_resources import safe_name


class Requirements:
    DEVELOPER_INSTALL="developer"
    NORMAL_INSTALL="normal"
    REQUIREMENTS = {
        DEVELOPER_INSTALL: "developer_installation.txt",
        NORMAL_INSTALL: "normal_installation.txt",
    }
    def __init__(self, requirement_path, package_name):
        self.requirement_path = requirement_path
        if not requirement_path.is_dir():
            print("ERROR: Requirements directory not found here: %s" % requirement_path)

        for filename in self.REQUIREMENTS.values():
            file_path = Path(self.requirement_path, filename)
            if not file_path.is_file():
                print("ERROR: Requirement file not found here: %s" % file_path)

        # FIXME: There must exist a better way to detect if the package is
        #        installed as "editable" or a normal package!

        self.src_path = Path(sys.prefix, "src")

        # pip install -e will change the package name via pkg_resources.safe_name
        # e.g.: "foo_bar" -> "foo-bar"
        package_dir_name = safe_name(package_name)

        src_bootstrap_env_path = Path(self.src_path, package_dir_name)

        if src_bootstrap_env_path.is_dir():
            print("%s is installed as editable here: %s" % (package_name, src_bootstrap_env_path))
            self.install_mode=self.DEVELOPER_INSTALL
        else:
            print("%s is installed as package." % package_name)
            self.install_mode=self.NORMAL_INSTALL

    @property
    def normal_mode(self):
        return self.install_mode == self.NORMAL_INSTALL

    def get_requirement_file_path(self):
        """
        :return: Path(.../bootstrap_env/requirements/<mode>_installation.txt)
        """
        filename = self.REQUIREMENTS[self.install_mode]
        requirement_file_path = Path(self.requirement_path, filename).resolve()
        return requirement_file_path
