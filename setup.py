from setuptools_scm import get_version as scm_get_version
from pycblosc import get_version_string as blosc_get_version
from distutils.core import setup
import semver

# Check that we have a reasonable recent C-Blosc library installed
blosc_version = blosc_get_version()
blosc_version = blosc_version[:blosc_version.rfind('.')]  # workaround for semver compliance
blosc_version_info = semver.parse_version_info(blosc_version)
if blosc_version_info.major != 1 or blosc_version_info.minor < 14:
    raise ValueError("Underlying C-Blosc should be 1.14 or higher")
print(blosc_version_info)

setup(
    name='pycblosc',
    version=scm_get_version(),
    py_modules=['pycblosc'],
)
