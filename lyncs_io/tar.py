"""
Interface for Tar format
"""

from os.path import exists, splitext
from .archive import split_filename
import tarfile
import tempfile


all_extensions = [
    '.tar',
    '.tar.bz2', '.tb2', '.tbz', '.tbz2', '.tz2',
    '.tar.gz', '.taz', '.tgz',
    '.tar.lz',
    '.tar.lzma', '.tlz',
    '.tar.lzo',
    '.tar.xz', '.txz',
    '.tar.Z', '.tZ', '.taZ',
    '.tar.zst', '.tzst'
    # source: wikipedia
]

modes = {
    # .gz, .bz2 and .xz should start with .tar
    # .tar was removed because of splitext()
    ':gz': ['.gz', '.taz', '.tgz'],
    ':bz2': ['.bz2', '.tb2', '.tbz', '.tbz2', '.tz2'],
    ':xz': ['.xz', '.txz'],
    ':': ['.tar'],
}

# TODO: Test for a valid filename format & test
# TODO: allow saving with no leaf (key) given & test [e.g. save(arr, tarball.tar)]
# TODO: fix issues with compression in append mode
# TODO: implement head()


# Given the tarball name, return the compression mode using modes
def save(arr, filename):
    """
    Save data from an array to a file in a tarball.

    Params:
    -------
    arr: The array to save the data from.
    tarball_name: The name of the tarball.
    filename: The name of the file to save the data to.
    """

    tarball_path, leaf = split_filename(filename)
    mode_suffix = _get_mode(tarball_path)

    # create Tar if doesn't exist - append if it does
    if exists(tarball_path):
        tar = tarfile.open(tarball_path, "a")
    else:
        tar = tarfile.open(tarball_path, "w" + mode_suffix)

    # A temporary directory is created to write a new file in.
    # The new file is then added to the tarball before being deleted.
    with tempfile.TemporaryDirectory() as tmpf:
        dat = open(tmpf + "/data.txt", 'w')
        for elt in arr:
            dat.write(str(elt) + '\n')
        dat.flush()  # flush data before adding the file to the archive
        tar.add(dat.name, arcname=leaf)
        dat.close()

    tar.close()


def load(filename):
    """
    Return an array from the data of a file in a tarball.
    """
    tarball_path, leaf = split_filename(filename)
    mode_suffix = _get_mode(tarball_path)

    if exists(tarball_path):
        tar = tarfile.open(tarball_path, "r" + mode_suffix)
    else:
        raise FileNotFoundError(f"{tarball_path} does not exist.")

    member = tar.getmember(leaf)
    f = tar.extractfile(member)
    arr = [x.decode('utf-8').replace('\n', '') for x in f.readlines()]

    # with tempfile.TemporaryDirectory() as tmpf:
        # extract to a temp location for reading
        # tar.extract(member, path=tmpf)
        # data_file = f"{tmpf}/{leaf}"
        # with open(data_file, "r") as dat:
        #     for line in dat.readlines():
        #         line = line.replace('\n', '')  # remove the newline character
        #         arr.append(line)

    tar.close()
    return arr


def head():
    pass


def _get_mode(filename):
    """
    Returns the mode (from modes) with which the tarball should be read/written as
    """
    ext = splitext(filename)[-1]
    for key, val in modes.items():
        if ext in val:
            return key
    raise ValueError(f"{ext} is not supported.")
