from subprocess import call
from setuptools import setup
from setuptools_scm import get_version as scm_get_version
from distutils.command.install_data import install_data


class blosc_install(install_data):
    def run(self):
        # Get a copy of the Blosc shared library via conan
        blosc_version = "1.14.0"
        with open("conanfile.txt", "w") as conanfile:
            conanfile.write("""
        [requires]
         c-blosc/v{}@francescalted/stable
        [options]
          c-blosc:shared=True
        [imports]
          bin, *.dll -> ./pycblosc
          lib, *.dylib* -> ./pycblosc
          lib, *.so* -> ./pycblosc
        """.format(blosc_version))
        # Copy the shared library for later install
        try:
            retcode = call("conan install conanfile.txt -r conan-center", shell=True)
            if retcode < 0:
                print("conan CLI was terminated by signal", -retcode)
            else:
                print("conan CLI returned", retcode)
        except OSError as e:
            print("conan CLI Execution failed:", e)

setup(
    name='pycblosc',
    version=scm_get_version(),
    description='A simple, low-level interface for C-Blosc',
    url='http://github.com/Blosc/pycblosc',
    author='Francesc Alted',
    author_email='francesc@blosc.org',
    license='BSD',
    packages=['pycblosc'],
    cmdclass = {"install_data": blosc_install},
    package_data={'pycblosc': ['libblosc.*']},
    zip_safe=False,
)
