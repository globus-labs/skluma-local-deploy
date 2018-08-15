
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


from topic_main import extract_topic
from ex_columns import process_structured_file  # Ignore pycharm red squiggle.
from file_type_extensions import freetext_type_list, image_type_list, tabular_type_list
import sqlite_helper  # TODO: Add this.


class RedundantMetadata(Exception):
    """ Throw this error if you're trying to get the same metadata element for a file an extra time. """

class UnreadableStructuredMetadata(Exception):
    """ Throw this error if the structured data extractor doesn't work. Means the file is failing. """

def main(debug = False, debug_file = None):


    # Just do one file.
    while True:
        #try:
            # Step 1. Pick a new file from the DB.
            #while True:

        #try:
        file_info = sqlite_helper.get_next_file()[0]  # Insert matplotlib that queries database.
        filename = file_info[0]
        metadata = file_info[1]
        last_extractor = file_info[2]

        # except Exception as e:
        #     print(e)
        #     print("Empty queue. Seeking again momentarily")
        #     time.sleep(5)  # Take a short, arbitrary nap :)
            # break # TODO: Add back break so we restart loop from beginning.

        # Get the extension from the file.
        if '.' in filename:
            extension = filename.split('.')[-1]
        else:
            extension = None

        print("Processing file of extension: " + extension + " " + filename)

        # *** Build extension override *** #
        ex_freetext = None
        ex_structured = None

        if extension.lower() in tabular_type_list:
            try:
                ex_structured = get_structured_metadata(filename, metadata)
            except:
                ex_structured = None

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
                    ex_structured = get_structured_metadata(filename, metadata)
                except:
                    ex_structured = None

        elif extension.lower() in image_type_list:
            # TODO: Add back image extractor.
            print("Image extractor here... ")

        metadata = ast.literal_eval(metadata)
        metadata["extractors"] = {}

        if ex_structured is not None and ex_structured != "None":
            new_metadata = ex_structured[0]
            metadata["extractors"]["ex_structured"] = new_metadata

        if ex_freetext is not None and ex_freetext != "None":
            new_metadata = ex_freetext[0]
            metadata["extractors"]["ex_freetext"] = new_metadata

        print("THE METADATA: " + str(metadata))

        sqlite_helper.update_db(filename, metadata, 'main1')


def get_freetext_metadata(filename, old_mdata):

    t0 = time.time()
    print("DOING WORK")
    metadata = extract_topic('file', filename)
    t1 = time.time()

    if 'ex_freetext' in old_mdata:
        print("There's already structured metadata for this file. ")
        return None  # Return nothing because no point.

    else:
        return (metadata, t1-t0)


def get_structured_metadata(filename, old_mdata):

    try:  # TODO: Are we updating ex_ls?

        print(filename)

        t0 = time.time()
        metadata = process_structured_file(filename)
        t1 = time.time()

        if 'ex_structured' in old_mdata:
            print("There's already structured metadata for this file. ")
            return None  # Return nothing because no point.

        else:
            return (metadata, t1-t0)

    except:  # If the metadata extraction utterly fails.
        print("Structured Extraction Failed. Terminating now. ")
        return None


main()
