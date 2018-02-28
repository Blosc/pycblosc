# pycblosc

A simple Python/CFFI interface for the C-Blosc library.

This tries to be a low level interface for C-Blosc.  Maybe in the future more high-level function could be added too.

This package is meant to be used in either Python 2 or 3.

## Simple usage

```

In [1]: import numpy as np

In [2]: import pycblosc as cb

# Create an input buffer
In [3]: a = np.arange(1000_000, dtype=np.int32)

# Create a buffer for compression
In [4]: b = np.empty(1000_000, dtype=np.int32)

# Create a buffer for decompression
In [5]: c = np.empty(1000_000, dtype=np.int32)

# Compress!
In [6]: cb.blosc_compress(7, 1, a.dtype.itemsize, a.size * a.dtype.itemsize, a, b, b.size * b.dtype.itemsize)
Out[6]: 36256

# Decompress!
In [7]: cb.blosc_decompress(b, c, c.size * c.dtype.itemsize)
Out[7]: 4000000

# Check for equality
In [8]: np.testing.assert_array_equal(a, c)

```

## Testing

```
$ python tests.py
```

## Installation

```
$ python setup.py install
```


## Authors

* **Francesc Alted**

