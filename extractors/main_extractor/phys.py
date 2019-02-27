
import os
import hashlib


def get_phys_metadata(filepath):
    """Crawl local filesystem. Return state (i.e, file list)
        :param directory string representing root level directory path """

    phys_metadata = {}

    # Get the extension from the file.
    if '.' in filepath:
        extension = filepath.split('.')[-1]
    else:
        extension = None

    size = os.stat(filepath).st_size
    sha256_hash = get_sha256_hash(filepath)

    phys_metadata["filepath"] = filepath
    phys_metadata["size"] = size
    phys_metadata["extension"] = extension
    phys_metadata["is_globus_uri"] = False

    phys_metadata["sha256_hash"] = sha256_hash

    return phys_metadata


def get_sha256_hash(filename):
    sha256_hash = hashlib.sha256()

    with open(filename, "rb") as f:

        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    hash_256 = sha256_hash.hexdigest()

    return hash_256
