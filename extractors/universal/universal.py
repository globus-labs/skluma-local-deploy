
import magic
import os
import time


def physical_attribute_extractor(filepath, stage_location):

    filepath = stage_location + filepath

    filesize = os.stat(filepath).st_size
    last_mod = os.stat(filepath).st_mtime
    thepath = filepath.split('/')[:-1]
    filename = filepath.split('/')[-1]

    mime_type = magic.from_file(filepath)



    # TODO: Check to see if extension.
    # TODO: Add perceived MIMETYPE.

    physical_metadata = {"filename": filename, "size": filesize, "mimetype": mime_type, "parent_dir": thepath,
                         "last_modified": last_mod}

    return physical_metadata


def get_metadata(filepath, stage_location):
    univ_metadata = physical_attribute_extractor(filepath, stage_location)

    time.sleep(5)

    return univ_metadata


