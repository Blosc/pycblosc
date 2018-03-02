import array
import copy
import unittest
import pycblosc as cblosc


class TestUM(unittest.TestCase):
    clevel = 5
    shuffle = cblosc.SHUFFLE
    N = 1000 * 1000
    itemsize = 4
    nbytes = N * itemsize
    arr = array.array('f', range(N))  # the array to compress
    carr = bytearray(N * itemsize)    # a buffer filled with zeros
    farr = array.array('f', carr)


    def setUp(self):
        self.arr1 = copy.copy(self.arr)   # the array to compress
        self.arr2 = copy.copy(self.farr)  # the final destination


    def test_compress_decompress(self):
        cblosc.compress(self.clevel, self.shuffle, self.itemsize, self.nbytes,
                        self.arr1, self.carr, self.nbytes)
        cblosc.decompress(self.carr, self.arr2, self.nbytes)
        self.assertEqual(self.arr1.tobytes(), self.arr2.tobytes())


    def test_compress_getitem(self):
        cblosc.compress(self.clevel, self.shuffle, self.itemsize, self.nbytes,
                        self.arr1, self.carr, self.nbytes)
        cblosc.getitem(self.carr, 1000, 10000, self.arr2)
        arr1 = self.arr1[1000:11000]
        arr2 = self.arr2[:10000]
        self.assertEqual(arr1.tobytes(), arr2.tobytes())


    def test_threads(self):
        cblosc.set_nthreads(2)
        n = cblosc.get_nthreads()
        self.assertEqual(n, 2)
        cblosc.set_nthreads(1)


    def test_set_compressor(self):
        cblosc.set_compressor('lz4hc')
        n = cblosc.get_compressor()
        self.assertEqual(n, 'lz4hc')
        cblosc.set_compressor(b'lz4')
        n = cblosc.get_compressor()
        self.assertEqual(n, 'lz4')


    def test_ratio(self):
        bcomp = cblosc.compress(self.clevel, self.shuffle, self.itemsize, self.nbytes,
                                self.arr1, self.carr, self.nbytes)
        ratio = self.nbytes / float(bcomp)
        self.assertGreater(ratio, 70)

    def test_buffer_sizes(self):
        cblosc.compress(self.clevel, self.shuffle, self.itemsize, self.nbytes,
                        self.arr1, self.carr, self.nbytes)
        nbytes, cbytes, blocksize = cblosc.cbuffer_sizes(self.carr)
        ratio = nbytes / cbytes
        self.assertGreater(ratio, 70)
        self.assertGreater(blocksize, 4096)

    def test_splitmode(self):
        bcomp = cblosc.compress(self.clevel, self.shuffle, self.itemsize, self.nbytes,
                                self.arr1, self.carr, self.nbytes)
        ratio1 = self.nbytes / float(bcomp)
        cblosc.set_splitmode(cblosc.NEVER_SPLIT)
        bcomp = cblosc.compress(self.clevel, self.shuffle, self.itemsize, self.nbytes,
                                self.arr1, self.carr, self.nbytes)
        ratio2 = self.nbytes / float(bcomp)
        self.assertGreater(ratio1, ratio2)


    def test_blocksize(self):
        n = cblosc.get_blocksize()
        cblosc.set_blocksize(2 * n)
        m = cblosc.get_blocksize()
        self.assertEqual(n, m)


    def test_compname(self):
        cname = cblosc.compcode_to_compname(0)
        self.assertEqual(cname, "blosclz")
        ccode = cblosc.compname_to_compcode(cname)
        self.assertEqual(ccode, 0)

    def test_list_compressors(self):
        clist = cblosc.list_compressors()
        if type(clist) is not str:
            clist = clist.decode()
        cname = clist.split(",")[0]
        self.assertEqual(cname, "blosclz")


if __name__ == '__main__':
    print("Running tests for PyCBlosc {} (C-Blosc {})".format(
        cblosc.__version__, cblosc.get_version_string()))

    unittest.main()
