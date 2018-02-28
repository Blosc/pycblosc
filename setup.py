from setuptools_scm import get_version
from distutils.core import setup


setup(
    name='pycblosc',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    version=get_version(),
    py_modules=['pycblosc'],
    )
