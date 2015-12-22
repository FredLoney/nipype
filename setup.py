import os
import re
import glob
import warnings
from setuptools import (setup, find_packages)


class InstallError(Exception):
    """Nipype installation error."""
    pass


def version(package):
    """
    :return: the package version as listed in the package `__init.py__`
        `__version__` variable.
    """
    # The version string parser.
    REGEXP = re.compile("""
       __version__   # The version variable
       \s*=\s*       # Assignment
       ['\"]         # Leading quote
       (.+)          # The version string capture group
       ['\"]         # Trailing quote
    """, re.VERBOSE)

    with open(os.path.join(package, '__init__.py')) as f:
       match = REGEXP.search(f.read())
       if not match:
           raise InstallError("The Nipype __version__ variable was not found")
       return match.group(1)


def requires():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def long_description():
    """
    :return: the README prologue
    """
    with open('README.rst') as f:
        lines = f.read().splitlines()
        for i, line in enumerate(lines):
            # The first section separator is dashes.
            if line.startswith('---'):
                # The previous line is the section header.
                # Grab the lines up to that line.
                return '\n'.join(lines[i-1]).strip()
        # The whole file is the prologue.
        return '\n'.join(lines).strip()


NAME                = 'nipype'
DESCRIPTION         = 'Neuroimaging in Python: Pipelines and Interfaces'
CLASSIFIERS         = ["Development Status :: 5 - Production/Stable",
                       "Environment :: Console",
                       "Intended Audience :: Science/Research",
                       "License :: OSI Approved :: BSD License",
                       "Operating System :: OS Independent",
                       "Programming Language :: Python",
                       "Topic :: Scientific/Engineering"]
URL                 = "http://nipy.org/nipype"
DOWNLOAD_URL        = "http://github.com/nipy/nipype/archives/master"
PLATFORMS           = "OS Independent"
LICENSE             = "BSD license"
AUTHOR              = "nipype developmers"
AUTHOR_EMAIL        = "nipy-devel@neuroimaging.scipy.org"
MAINTAINER          = "nipype developers"
MAINTAINER_EMAIL    = "nipy-devel@neuroimaging.scipy.org"


setup(name=NAME,
      version = version('nipype'),
      description=DESCRIPTION,
      long_description = long_description(),
      url=URL,
      download_url=DOWNLOAD_URL,
      platforms=PLATFORMS,
      license=LICENSE,
      classifiers=CLASSIFIERS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      packages = find_packages(),
      include_package_data=True,
      install_requires=requires())
