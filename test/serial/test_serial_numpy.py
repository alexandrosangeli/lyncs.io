import lyncs_io as io
import numpy as np

from lyncs_io.testing import dtype_loop, shape_loop, tempdir
from lyncs_utils import prod


@dtype_loop
@shape_loop
def test_serial_numpy(tempdir, dtype, shape):
    arr = np.random.rand(*shape).astype(dtype)

    ftmp = tempdir + "/foo.npy"
    io.save(arr, ftmp)
    assert (arr == io.load(ftmp)).all()
    assert (arr == io.load(ftmp, format="numpy")).all()
    assert io.load(ftmp).shape == io.head(ftmp)["shape"]
    assert io.load(ftmp).dtype == io.head(ftmp)["dtype"]

    # 1D or 2D arrays only for savetxt
    if len(arr.shape) <= 2:
        ftmp = tempdir + "/foo.txt"
        io.save(arr, ftmp)
        assert (arr == io.load(ftmp)).all()
        assert (arr == io.load(ftmp, format="ascii")).all()

    ftmp = tempdir + "/foo.npz"
    io.save(arr, ftmp)
    assert (arr == io.load(ftmp)["arr_0"]).all()
    assert (arr == io.load(ftmp + "/arr_0", format="numpyz")).all()
    assert list(io.load(ftmp)) == list(io.head(ftmp))
    assert io.load(ftmp)["arr_0"].shape == io.head(ftmp)["arr_0"]["shape"]
    assert io.load(ftmp)["arr_0"].dtype == io.head(ftmp)["arr_0"]["dtype"]

    ftmp = tempdir + "/foo.npz/arr"
    io.save(arr, ftmp)
    assert (arr == io.load(ftmp)).all()
    assert (arr == io.load(ftmp, format="numpyz")).all()
    assert io.load(ftmp).shape == io.head(ftmp)["shape"]
    assert io.load(ftmp).dtype == io.head(ftmp)["dtype"]
