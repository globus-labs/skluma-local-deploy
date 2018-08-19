
""" This script is the main runner of the main file metadata extractor. Starts with information from the sampler
    and continuously puts the file through relevant extractors. Updates in RDS db as it goes.

    Author: Tyler J. Skluzacek
    Last Edited: 08/14/2018
"""

import ast
import nltk
import sys
import time

nltk.download("punkt")

sys.path.insert(0,'/src/topic')
sys.path.insert(0,'/src/columns')
sys.path.insert(0,'/src/structured')


from topic_main import extract_topic
from ex_nc import extract_netcdf_metadata
from ex_columns import process_structured_file  # Ignore pycharm red squiggle.
from file_type_extensions import freetext_type_list, image_type_list, tabular_type_list, structured_type_list
import sqlite_helper


class RedundantMetadata(Exception):
    """ Throw this error if you're trying to get the same metadata element for a file an extra time. """

class UnreadableStructuredMetadata(Exception):
    """ Throw this error if the structured data extractor doesn't work. Means the file is failing. """

def main(debug = False, debug_file = None):


    # Just do one file.
    while True:
        file_info = sqlite_helper.get_next_file()[0]  # Insert matplotlib that queries database.
        filename = file_info[0]
        metadata = file_info[1]
        last_extractor = file_info[2]

        # Get the extension from the file.
        if '.' in filename:
            extension = filename.split('.')[-1]
        else:
            extension = None

        # *** Build extension override *** #
        ex_freetext = None
        ex_tabular = None
        ex_structured = None

        if extension.lower() in tabular_type_list:
            try:
                ex_tabular = get_tabular_metadata(filename, metadata)
            except:
                ex_tabular = None

                try:
                    ex_freetext = get_freetext_metadata(filename, metadata)
                except:
                    ex_freetext = None

        elif extension.lower() in freetext_type_list:
            try:
                ex_freetext = get_freetext_metadata(filename, metadata)
            except:
                ex_freetext = None
                try:
                    ex_tabular = get_tabular_metadata(filename, metadata)
                except:
                    ex_tabular = None

        elif extension.lower() in image_type_list:
            # TODO: Add back image extractor.
            print("Image extractor here... ")

        elif extension.lower() == "nc":
            try:
                ex_structured = get_netcdf_metadata(filename, metadata)
            except:
                # print("NETCDF Failed, you fuck. ")
                ex_structured = None
            # try:
            #     ex_freetext = get_freetext_metadata(filename, metadata)
            # except:
            #     ex_freetext = None

        metadata = ast.literal_eval(metadata)
        metadata["extractors"] = {}

        if ex_tabular is not None and ex_tabular != "None":
            new_metadata = ex_tabular[0]
            metadata["extractors"]["ex_tabular"] = new_metadata

        if ex_freetext is not None and ex_freetext != "None":
            new_metadata = ex_freetext[0]
            metadata["extractors"]["ex_freetext"] = new_metadata

        if ex_structured is not None and ex_structured != "None":
            new_metadata = ex_structured[0]
            metadata["extractors"]["ex_structured"] = new_metadata

        sqlite_helper.update_db(filename, metadata, 'main1')


def get_freetext_metadata(filename, old_mdata):

    t0 = time.time()
    metadata = extract_topic('file', filename)
    t1 = time.time()

    if 'ex_freetext' in old_mdata:
        print("There's already structured metadata for this file. ")
        return None  # Return nothing because no point.

    else:
        return (metadata, t1-t0)


def get_tabular_metadata(filename, old_mdata):

    try:

        metadata = process_structured_file(filename)

        if 'ex_tabular' in old_mdata:
            print("There's already structured metadata for this file. ")
            return None  # Return nothing because no point.

        else:
            return (metadata, 0)

    except:  # If the metadata extraction utterly fails.
        print("Structured Extraction Failed. Terminating now. ")
        return None

def get_netcdf_metadata(filename, old_mdata):
    try:

        with open(filename, 'rw') as f:
            metadata = extract_netcdf_metadata(f)

        if 'ex_netcdf' in old_mdata:
            print("Already NetCDF metadata for this file.")
            return None

        else:
            return(metadata, 0)

    except:
        print("NetCDF extraction Failed. Terminating now . ")
        return None


main()