import os
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.build import build
from pathlib import Path
import shutil
import sys


extension = Extension(
    name="pyoorb",
    sources=["pyoorb.f90", "pyoorb.pyf"],
    include_dirs=["../build"]
)


class PyoorbBuildExt(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        try:
            self.spawn(["./configure", "gfortran", "opt",
                        "--with-pyoorb",
                        f"--with-f2py={shutil.which('f2py')}",
                        f"--with-python={sys.executable}"])
            self.spawn(["make", "-j4"])
            self.spawn(["make", "pyoorb", "-j4"])
        finally:
            os.chdir("./python")

        src = "../lib/" + self.get_ext_filename(ext.name)
        dst = self.get_ext_fullpath(ext.name)
        self.mkpath(os.path.dirname(dst))
        self.copy_file(src, dst)


class PyoorbBuild(build):
    """Overrides setuptools default which treats the 'build' directory
    as a Python build directory; that treatment results in all files
    in build/ getting pruned out of source distributions, but we want
    to keep build/Makefile and build/make.depends. So, the build
    directory is changed to build_py.

    """
    def initialize_options(self):
        super().initialize_options()
        self.build_base = "build_py"


def deduce_version():
    # This is a gnarly hack, but it ensures consistency.
    stdout = subprocess.PIPE
    cmd_output = subprocess.run(
        ["./build-tools/compute-version.sh",  "-u"],
        stdout=stdout,
    )
    cmd_output.check_returncode()
    return cmd_output.stdout.decode("utf8").strip()


setup(
    name='pyoorb',
    maintainer="oorb developers",
    maintainer_email="oorb@googlegroups.com",
    description="An open-source orbit-computation package for Solar System objects. ",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/oorb/oorb",
    author="Mikael Granvik et al.",
    download_url="https://pypi.python.org/pypi/oorb",
    project_urls={
        "Bug Tracker": "https://github.com/oorb/oorb/issues",
        "Source Code": "https://github.com/oorb/oorb",
    },
    version=deduce_version(),
    ext_modules=[extension],
    install_requires=["numpy"],
    license="GPL3",
    cmdclass={
        "build_ext": PyoorbBuildExt,
        "build": PyoorbBuild,
    }
)
