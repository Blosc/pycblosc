# Simple CFFI wrapper for the C-Blosc library

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    from setuptools_scm import get_version
    __version__ = get_version()


from cffi import FFI

ffi = FFI()
ffi.cdef(
    """
    void blosc_init(void);

    void blosc_destroy(void);

    int blosc_compress(int clevel, int doshuffle, size_t typesize, size_t nbytes, const void* src, void* dest,
                       size_t destsize);

    int blosc_decompress(const void* src, void* dest, size_t destsize);

    int blosc_getitem(const void* src, int start, int nitems, void* dest);

    int blosc_get_nthreads(void);

    int blosc_set_nthreads(int nthreads);

    char* blosc_get_compressor(void);

    int blosc_set_compressor(const char* compname);

    int blosc_compcode_to_compname(int compcode, char** compname);

    int blosc_compname_to_compcode(const char* compname);

    char* blosc_list_compressors(void);

    char* blosc_get_version_string(void);

    int blosc_get_complib_info(char* compname, char** complib, char** version);

    int blosc_free_resources(void);

    void blosc_cbuffer_sizes(const void* cbuffer, size_t* nbytes, size_t* cbytes, size_t* blocksize);

    void blosc_cbuffer_metainfo(const void* cbuffer, size_t* typesize, int* flags);

    void blosc_cbuffer_versions(const void* cbuffer, int* version, int* versionlz);

    char* blosc_cbuffer_complib(const void* cbuffer);

    int blosc_get_blocksize(void);

    void blosc_set_blocksize(size_t blocksize);

    void blosc_set_splitmode(int splitmode);
    """
)

C = ffi.dlopen("blosc")

# Most used constants
NOSHUFFLE = 0
SHUFFLE = 1
BITSHUFFLE = 2
ALWAYS_SPLIT = 1
NEVER_SPLIT = 2
AUTO_SPLIT = 3
FORWARD_COMPAT_SPLIT = 4


def init():
    return C.blosc_init()


def destroy():
    return C.blosc_destroy()


def compress(clevel, doshuffle, typesize, nbytes, src, dest, destsize):
    src = ffi.from_buffer(src)
    dest = ffi.from_buffer(dest)
    return C.blosc_compress(clevel, doshuffle, typesize, nbytes, src, dest, destsize)


def decompress(src, dest, destsize):
    src = ffi.from_buffer(src)
    dest = ffi.from_buffer(dest)
    return C.blosc_decompress(src, dest, destsize)


def getitem(src, start, nitems, dest):
    src = ffi.from_buffer(src)
    dest = ffi.from_buffer(dest)
    return C.blosc_getitem(src, start, nitems, dest)


def get_nthreads():
    return C.blosc_get_nthreads()


def set_nthreads(nthreads):
    return C.blosc_set_nthreads(nthreads)


def get_compressor():
    return ffi.string(C.blosc_get_compressor()).decode()


def set_compressor(compname):
    if type(compname) is str:
        compname = compname.encode()
    compname = ffi.new("char[]", compname)
    return C.blosc_set_compressor(compname)


def compcode_to_compname(compcode):
    compname = ffi.new("char **")
    C.blosc_compcode_to_compname(compcode, compname)
    compname = ffi.string(compname[0])
    if type(compname) is not str:
        compname = compname.decode()
    return compname


def compname_to_compcode(compname):
    if type(compname) is str:
        compname = compname.encode()
    compname = ffi.new("char[]", compname)
    return C.blosc_compname_to_compcode(compname)


def list_compressors():
    return ffi.string(C.blosc_list_compressors())


def get_version_string():
    version = ffi.string(C.blosc_get_version_string())
    if type(version) is not str:
        version = version.decode()
    return version


def get_complib_info(compname):
    complib = ffi.new("char **")
    version = ffi.new("char **")
    return (C.blosc_get_complib_info(compname, complib, version),
            ffi.string(complib[0]),
            ffi.string(version[0]))


def free_resources():
    return C.blosc_free_resources()


def cbuffer_sizes(cbuffer):
    nbytes = ffi.new("size_t *")
    cbytes = ffi.new("size_t *")
    blocksize = ffi.new("size_t *")
    cbuffer = ffi.from_buffer(cbuffer)
    C.blosc_cbuffer_sizes(cbuffer, nbytes, cbytes, blocksize)
    return nbytes[0], cbytes[0], blocksize[0]


def cbuffer_metainfo(cbuffer):
    typesize = ffi.new("size_t *")
    flags = ffi.new("int *")
    cbuffer = ffi.from_buffer(cbuffer)
    C.blosc_cbuffer_metainfo(cbuffer, typesize, flags)
    return typesize[0], list((0, 1)[flags[0] >> j & 1] for j in range(3, -1, -1))


def cbuffer_versions(cbuffer):
    version = ffi.new("int *")
    versionlz = ffi.new("int *")
    cbuffer = ffi.from_buffer(cbuffer)
    C.blosc_cbuffer_versions(cbuffer, version, versionlz)
    return version[0], versionlz[0]


def cbuffer_complib(cbuffer):
    cbuffer = ffi.from_buffer(cbuffer)
    return ffi.string(C.blosc_cbuffer_complib(cbuffer))


def get_blocksize():
    return C.blosc_get_blocksize()


def set_blocksize(blocksize):
    return C.blosc_set_blocksize(blocksize)


def set_splitmode(splitmode):
    return C.blosc_set_splitmode(splitmode)
