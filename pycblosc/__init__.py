"""
Simple CFFI wrapper for the C-Blosc library.
"""

from pkg_resources import get_distribution, DistributionNotFound
from distutils.version import LooseVersion

from .pycblosc import *


# Check that we have a reasonable recent C-Blosc library installed
min_blosc_version = LooseVersion("1.14.0")
blosc_version = LooseVersion(get_version_string())
if blosc_version < min_blosc_version:
    raise ValueError("Underlying C-Blosc should be %s or higher" % min_blosc_version)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    from setuptools_scm import get_version as scm_get_version
    __version__ = scm_get_version()
