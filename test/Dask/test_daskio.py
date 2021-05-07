import numpy
import dask
import dask.array as da
from dask.distributed import Client

from lyncs_utils import prod
from lyncs_io.dask_io import DaskIO
import lyncs_io as io

from lyncs_io.testing import domain_loop, workers_loop, chunksize_loop, tempdir


@domain_loop
@chunksize_loop
@workers_loop
def test_daskio_load(tempdir, domain, chunksize, workers):

    client = Client(n_workers=workers, threads_per_worker=1)

    ftmp = tempdir + "foo.npy"
    size = prod(domain)
    x_ref = numpy.arange(0, size).reshape(domain)
    x_ref_out = io.save(x_ref, ftmp)

    daskio = DaskIO(ftmp)

    header = io.numpy.head(ftmp)
    # chunks should have the same length as domain
    chunks = tuple(chunksize for a in range(len(domain)))

    x_lazy_in = daskio.load(
        header["shape"],
        header["dtype"],
        header["_offset"],
        chunks=chunks,
        order="F" if header["_fortran_order"] else "C",
    )

    assert isinstance(x_lazy_in, da.Array)
    assert (x_ref == x_lazy_in.compute()).all()

    client.shutdown()


@domain_loop
@chunksize_loop
@workers_loop
def test_daskio_write(tempdir, domain, chunksize, workers):

    client = Client(n_workers=workers, threads_per_worker=1)

    ftmp = tempdir + "foo.npy"
    size = prod(domain)
    # chunks should have the same length as domain
    chunks = tuple(chunksize for a in range(len(domain)))

    x_lazy = da.arange(0, size).reshape(domain).rechunk(chunks=chunks)
    x_ref = numpy.arange(0, size).reshape(domain)

    daskio = DaskIO(ftmp)
    x_lazy_out = daskio.save(x_lazy)
    assert isinstance(x_lazy_out, da.Array)

    x_out = x_lazy_out.compute()
    x_ref_in = io.load(ftmp)

    assert (x_ref == x_out).all()
    assert (x_ref == x_ref_in).all()

    client.shutdown()
