from setuptools import setup
from setuptools_scm import get_version as scm_get_version

setup(
    name='pycblosc',
    version=scm_get_version(),
    description='A simple, low-level interface for C-Blosc',
    url='http://github.com/Blosc/pycblosc',
    author='Francesc Alted',
    author_email='francesc@blosc.org',
    license='BSD',
    packages=['pycblosc'],
    zip_safe=False)
