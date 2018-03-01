"""
Simple CFFI wrapper for the C-Blosc library.

This is a low-level Python wrapper for the public API of the C-Blosc library.
Most of the functions have the same parameters and return values than their
C-Blosc counterparts.  However, there are some exceptions in order to adapt
to usual Python idioms.

For a detailed info, see the docstrings on the different functions.
"""

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

    int blosc_compress(int clevel, int doshuffle, size_t typesize, size_t nbytes,
                       const void* src, void* dest, size_t destsize);

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

    void blosc_cbuffer_sizes(const void* cbuffer, size_t* nbytes, size_t* cbytes,
                             size_t* blocksize);

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
MIN_HEADER_LENGTH = 16
MAX_OVERHEAD = MIN_HEADER_LENGTH
NOSHUFFLE = 0
SHUFFLE = 1
BITSHUFFLE = 2
ALWAYS_SPLIT = 1
NEVER_SPLIT = 2
AUTO_SPLIT = 3
FORWARD_COMPAT_SPLIT = 4


def init():
    """
    Initialize the Blosc library environment.

    You must call this previous to any other Blosc call, unless you want
    Blosc to be used simultaneously in a multi-threaded environment, in
    which case you should *exclusively* use the
    blosc_compress_ctx()/blosc_decompress_ctx() pair (see below).

    Returns:
        None
    """
    return C.blosc_init()


def destroy():
    """
    Destroy the Blosc library environment.

    You must call this after to you are done with all the Blosc calls,
    unless you have not used `blosc_init()` before.

    Returns:
        None
    """
    return C.blosc_destroy()


def compress(clevel, doshuffle, typesize, nbytes, src, dest, destsize):
    """
    Compress a block of data in the `src` buffer to `dest` buffer.

    Compression is memory safe and guaranteed not to write the `dest`
    buffer beyond what is specified in `destsize`.

    Args:
        clevel (int): The desired compression level.
            Must be a number between 0 (no compression) and 9 (maximum compression).
        doshuffle (int): Specifies whether the shuffle compression filter should be applied or not.
            BLOSC_NOSHUFFLE means not applying it, BLOSC_SHUFFLE means applying it at
            a byte level and BLOSC_BITSHUFFLE at a bit level (slower but may achieve
            better entropy alignment).
        typesize (int): The number of bytes for the atomic type in binary `src` buffer.
            This is mainly useful for the shuffle filter.
            For implementation reasons, only a 1 < `typesize` < 256 will allow the
            shuffle filter to work.  When `typesize` is not in this range, shuffle
            will be silently disabled.
        nbytes (int): The size of `src` buffer in bytes.
        src (object): The source buffer.
            Can be any Python object that supports the buffer protocol.
        dest (object): The destination buffer.
            Can be any Python object that supports the buffer protocol.
            The `dest` buffer must have at least the size of `destsize`.  Blosc
            guarantees that if you set `destsize` to, at least,
            (`nbytes` + BLOSC_MAX_OVERHEAD), the compression will always succeed.
            The `src` buffer and the `dest` buffer can not overlap.
        destsize (int): The size of `dest` buffer in bytes.

    Returns:
        int: The size of the compressed block.

            If `src` buffer cannot be compressed into `destsize`, the return
            value is zero and you should discard the contents of the `dest`
            buffer.

            A negative return value means that an internal error happened.  This
            should never happen.  If you see this, please report it back
            together with the buffer data causing this and compression settings.

    Environment variables:
        `blosc_compress()` honors different environment variables to control
        internal parameters without the need of doing that programatically.
        Here are the ones supported:

        * BLOSC_CLEVEL=(INTEGER): This will overwrite the `clevel` parameter
            before the compression process starts.

        * BLOSC_SHUFFLE=[NOSHUFFLE | SHUFFLE | BITSHUFFLE]: This will
            overwrite the `doshuffle` parameter before the compression process
            starts.

        * BLOSC_TYPESIZE=(INTEGER): This will overwrite the `typesize`
            parameter before the compression process starts.

        * BLOSC_COMPRESSOR=[BLOSCLZ | LZ4 | LZ4HC | SNAPPY | ZLIB]: This will
            call blosc_set_compressor(BLOSC_COMPRESSOR) before the compression
            process starts.

        * BLOSC_NTHREADS=(INTEGER): This will call
            blosc_set_nthreads(BLOSC_NTHREADS) before the compression process
            starts.

        * BLOSC_BLOCKSIZE=(INTEGER): This will call
            blosc_set_blocksize(BLOSC_BLOCKSIZE) before the compression process
            starts.  *NOTE:* The blocksize is a critical parameter with
            important restrictions in the allowed values, so use this with care.

        * BLOSC_NOLOCK=(ANY VALUE): This will call blosc_compress_ctx() under
            the hood, with the `compressor`, `blocksize` and
            `numinternalthreads` parameters set to the same as the last calls to
            blosc_set_compressor(), blosc_set_blocksize() and
            blosc_set_nthreads().  BLOSC_CLEVEL, BLOSC_SHUFFLE, BLOSC_TYPESIZE
            environment vars will also be honored.

        * BLOSC_SPLITMODE=[ FORWARD_COMPAT | AUTO | ALWAYS | NEVER ]:
            This will call blosc_set_splitmode() with the different supported values.
            See blosc_set_splitmode() docstrings for more info on each mode.

    """
    src = ffi.from_buffer(src)
    dest = ffi.from_buffer(dest)
    return C.blosc_compress(clevel, doshuffle, typesize, nbytes, src, dest, destsize)


def decompress(src, dest, destsize):
    """
    Decompress a block of compressed data in the `src` buffer to `dest` buffer.

    The `src` buffer and the `dest` buffer can not overlap.

    Decompression is memory safe and guaranteed not to write the `dest`
    buffer beyond what is specified in `destsize`.

    Args:
        src (object): The source buffer containing compressed data.
            Can be any Python object that supports the buffer protocol.
        dest (object): The destination buffer.
            Can be any Python object that supports the buffer protocol.
        destsize (int): The size of `dest` buffer in bytes.

    Returns:
        int: The size of the decompressed block
            If an error occurs, e.g. the compressed data is corrupted or the
            output buffer is not large enough, then 0 (zero) or a negative value
            will be returned instead.

    Environment variables:
        `blosc_decompress()` honors different environment variables to control
        internal parameters without the need of doing that programatically.
        Here are the ones supported:

        * BLOSC_NTHREADS=(INTEGER): This will call
            `blosc_set_nthreads(BLOSC_NTHREADS)` before the proper decompression
            process starts.

        * BLOSC_NOLOCK=(ANY VALUE): This will call `blosc_decompress_ctx()`
            under the hood, with the `numinternalthreads` parameter set to the
            same value as the last call to `blosc_set_nthreads()`.

    """
    src = ffi.from_buffer(src)
    dest = ffi.from_buffer(dest)
    return C.blosc_decompress(src, dest, destsize)


def getitem(src, start, nitems, dest):
    """
    Get `nitems` (of typesize size) in `src` buffer starting in `start`.

    The items are returned in `dest` buffer, which has to have enough
    space for storing all items.

    Args:
        src (object): The source buffer containing compressed data.
            Can be any Python object that supports the buffer protocol.
        start (int): The start of the items to fetch.
        nitems (int): The number of items to fetch.
        dest (object): The destination buffer.
            Can be any Python object that supports the buffer protocol.

    Returns:
        int: The number of bytes copied to `dest` or a negative value if
            some error happens.
    """
    src = ffi.from_buffer(src)
    dest = ffi.from_buffer(dest)
    return C.blosc_getitem(src, start, nitems, dest)


def get_nthreads():
    """
    Get the current number of threads used for compression/decompression.

    Returns:
        int: The current number of threads used for compression/decompression.
    """
    return C.blosc_get_nthreads()


def set_nthreads(nthreads):
    """
    Initialize a pool of threads for compression/decompression.

    If `nthreads` is 1, then the serial version is chosen and a possible
    previous existing pool is ended.  If this is not called, `nthreads`
    is set to 1 internally.

    Args:
        nthreads: The number of threads for creating the new pool.

    Returns:
        int: The previous number of threads in the pool.

    """
    return C.blosc_set_nthreads(nthreads)


def get_compressor():
    """
    Get the current compressor that is used for compression.

    Returns:
        str: The name of the current compressor.

    """
    return ffi.string(C.blosc_get_compressor()).decode()


def set_compressor(compname):
    """
    Select the compressor to be used.

    The supported ones are "blosclz", "lz4", "lz4hc", "snappy", "zlib"
    and "ztsd".  If this function is not called, then "blosclz" is
    used by default.

    Args:
        compname (str): The name of the compressor.

    Returns:
        int: In case the compressor is not recognized, or there is not support
            for it in this build, it returns a -1.  Else it returns the code for
            the compressor (>=0).
    """
    if isinstance(compname, str):
        compname = compname.encode()
    compname = ffi.new("char[]", compname)
    return C.blosc_set_compressor(compname)


def compcode_to_compname(compcode):
    """
    Get the `compname` associated with the `compcode`.

    Args:
        compcode: The code of the compressor.

    Returns:
        str: the compressor name associated with the compressor code.
            If the compressor name is not recognized, or there is not support
            for it in this build, `None` is returned instead.
    """
    compname = ffi.new("char **")
    code = C.blosc_compcode_to_compname(compcode, compname)
    if code < 0:
        return None
    compname = ffi.string(compname[0])
    if not isinstance(compname, str):
        compname = compname.decode()
    return compname


def compname_to_compcode(compname):
    """
    Get the compressor code associated with the compressor name.


    Args:
        compname: The name of the compressor.

    Returns:
        int: The code of the compressor.  If the compressor name
            is not recognized, or there is not support for it in this build,
            a -1 is returned instead.
    """
    if isinstance(compname, str):
        compname = compname.encode()
    compname = ffi.new("char[]", compname)
    return C.blosc_compname_to_compcode(compname)


def list_compressors():
    """
    Get a list of compressors supported in the current build.

    This function does not leak, so you should not free() the returned
    list.

    Returns:
        str:  Concatenation of "blosclz", "lz4", "lz4hc", "snappy", "zlib"
            or "zstd "separated by commas, depending on which ones are present
            in the build.
    """
    return ffi.string(C.blosc_list_compressors())


def get_version_string():
    """
    Return the version of the C-Blosc library in string format.

    Returns:
        str: The version of the C-Blosc library.
    """
    version = ffi.string(C.blosc_get_version_string())
    if not isinstance(version, str):
        version = version.decode()
    return version


def get_complib_info(compname):
    """
    Get info from compression libraries included in the current build.

    Args:
        compname: The compressor name that you want info from.

    Returns:
        tuple: A tuple (`complib`, `version`) with compression library name
            and version in string format.

            If the compressor is not supported, `None` is returned instead.

    Note:
        This Python implementation may leak the space for storing the `complib`
        and `version` strings, so do not abuse of this call.
    """
    complib = ffi.new("char **")
    version = ffi.new("char **")
    code = C.blosc_get_complib_info(compname, complib, version)
    if code < 0:
        return None
    return ffi.string(complib[0]), ffi.string(version[0])


def free_resources():
    """
    Free possible memory temporaries and thread resources.

    Use this when you are not going to use Blosc for a long while.

    Returns:
        int: In case of problems releasing the resources, it returns
            a negative number, else it returns 0.
    """
    return C.blosc_free_resources()


def cbuffer_sizes(cbuffer):
    """
    Retrieve information about a compressed buffer (`cbuffer`).

    Args:
        cbuffer (object): The compressed buffer.

    Returns:
        tuple: (`nbytes`, `cbytes`, `blocksize`). `nbytes` is the number of
            uncompressed bytes, `cbytes` is the number of compressed bytes,
            whereas `blocksize` is used internally for doing the compression by blocks.

            If the format is not supported by the library, all these values will be
            zeros.

    Note:
        You only need to pass the first BLOSC_MIN_HEADER_LENGTH bytes of a
        compressed buffer for this call to work.
    """
    nbytes = ffi.new("size_t *")
    cbytes = ffi.new("size_t *")
    blocksize = ffi.new("size_t *")
    cbuffer = ffi.from_buffer(cbuffer)
    C.blosc_cbuffer_sizes(cbuffer, nbytes, cbytes, blocksize)
    return nbytes[0], cbytes[0], blocksize[0]


def cbuffer_metainfo(cbuffer):
    """
    Retrieve meta-information about a compressed buffer (`cbuffer`).

    Args:
        cbuffer (object): The compressed buffer.

    Returns:
        tuple: (`typesize`, `flags`). `typesize` is the size of the
            type, whereas `flags` is a list of booleans.

            The list of booleans in `flags` is currently made of 3 elements:
            * 0: whether the shuffle filter has been applied or not
            * 1: whether the internal buffer is a pure memcpy or not
            * 2: whether the bit shuffle filter has been applied or not

            If the format is not supported by the library, all output arguments will be
            filled with zeros (or False values for the `flags` list).

    Note:
        You only need to pass the first BLOSC_MIN_HEADER_LENGTH bytes of a
        compressed buffer for this call to work.
    """
    typesize = ffi.new("size_t *")
    flags = ffi.new("int *")
    cbuffer = ffi.from_buffer(cbuffer)
    C.blosc_cbuffer_metainfo(cbuffer, typesize, flags)
    return typesize[0], list((False, True)[flags[0] >> j & 1] for j in range(3, -1, -1))


def cbuffer_versions(cbuffer):
    """
    Get compressor version information on a compressed buffer (`cbuffer`).

    Args:
        cbuffer (object): The compressed buffer.

    Returns:
        tuple: (`version`, `compversion`). `version` is the  C-Blosc format
            version and `compversion` is the format for the internal compressor
            used.
    """
    version = ffi.new("int *")
    versionlz = ffi.new("int *")
    cbuffer = ffi.from_buffer(cbuffer)
    C.blosc_cbuffer_versions(cbuffer, version, versionlz)
    return version[0], versionlz[0]


def cbuffer_complib(cbuffer):
    """
    Get the compressor library/format used in a compressed buffer.

    Args:
        cbuffer (object): The compressed buffer.

    Returns:
        str: The compressor library/format used in a compressed buffer.
    """
    cbuffer = ffi.from_buffer(cbuffer)
    return ffi.string(C.blosc_cbuffer_complib(cbuffer))


def get_blocksize():
    """
    Get the internal blocksize to be used during compression.

    Returns:
        int: The internal blocksize to used during compression.
            0 means that an automatic blocksize is computed internally
            (the default).
    """
    return C.blosc_get_blocksize()


def set_blocksize(blocksize):
    """
    Force the use of a specific blocksize.

    The blocksize is a critical parameter with important restrictions in
    the allowed values, so use this with care.

    Args:
        blocksize (int): The value for the blocksize.  If 0, an automatic
            blocksize will be used (the default).

    Returns:
        None
    """
    return C.blosc_set_blocksize(blocksize)


def set_splitmode(splitmode):
    """
    Set the split mode.

    FORWARD_COMPAT offers reasonably forward compatibility, AUTO_SPLIT is
    for nearly optimal results (based on heuristics), NEVER_SPLIT and
    ALWAYS_SPLIT are for the user experimenting when trying to get best
    compression ratios and/or speed.

    If not called, the default mode is FORWARD_COMPAT_SPLIT.

    Args:
        splitmode (int): The split mode.  Can be one of these:
            *  BLOSC_FORWARD_COMPAT_SPLIT
            *  BLOSC_AUTO_SPLIT
            *  BLOSC_NEVER_SPLIT
            *  BLOSC_ALWAYS_SPLIT

    Returns:
        None

    """
    return C.blosc_set_splitmode(splitmode)
