from .pycblosc import *

from distutils.version import LooseVersion

min_blosc_version = LooseVersion("1.14.0")

# Check that we have a reasonable recent C-Blosc library installed
blosc_version = LooseVersion(get_version_string())
if blosc_version < min_blosc_version:
    raise ValueError("Underlying C-Blosc should be %s or higher" % min_blosc_version)
