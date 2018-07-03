
""" This script is the main runner of the main file metadata extractor. Starts with information from the sampler
    and continuously puts the file through relevant extractors. Updates in RDS db as it goes.

    Author: Tyler J. Skluzacek
    Last Edited: 01/31/2018
"""

import decimal
import json
import nltk
import requests
import sys
import time
import urllib

nltk.download("punkt")

# sys.path.insert(0, 'src/columns')
# sys.path.insert(0, 'src/topic')
sys.path.insert(0,'topic')
sys.path.insert(0,'columns')

from topic_main import extract_topic
from ex_columns import extract_columnar_metadata  # Ignore pycharm red squiggle.
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
        while True:
            try:
                file_info = sqlite_helper.get_next_file()  # Insert matplotlib that queries database.
                break

            except:
                print("Empty queue. Seeking again momentarily")
                time.sleep(5)

        # Pick apart the variable names for sanity's sake.
        filename = file_info[0]
        print(filename)
        metadata = file_info[1]
        ex_ls = file_info[2]
        total_time = file_info[3]
        last_extractor = file_info[4]
        real_path = file_info[5]

        try:
            ex_structured = get_structured_metadata(filename, metadata)
        except:
            ex_structured = None
        # if ex_structured == None or ex_structured == "None":

        try:
            ex_freetext = get_freetext_metadata(filename, metadata)
        except:
            ex_freetext = None

        if ex_freetext != None:
            new_metadata = ex_freetext[0]
            added_time = ex_freetext[1]

            total_time += decimal.Decimal(str(added_time))  # Total time spent extracting this file.

            try: #TODO: Is this a bad try/except?
                metadata["extractors"]["ex_freetext"] = new_metadata["ex_freetext"]
            except:
                pass
        if ex_structured != None or ex_structured != "None":
            new_metadata = ex_structured[0]
            added_time = ex_structured[1]

            total_time += decimal.Decimal(str(added_time))  # Total time spent extracting this file.
            metadata["extractors"]["ex_structured"] = new_metadata

        # Now update metadata in RDS.
        print("Decoding URL now...")
        new_url = metadata["metadata"]["file"]["path"].replace('/home/skluzacek/Downloads/', '')
        print(new_url)
        new_url = urllib.unquote(new_url).decode('utf8')
        print(new_url)

        metadata["metadata"]["file"]["path"] = new_url
        metadata["metadata"]["file"]["size"] = str(metadata["metadata"]["file"]["size"])

        metadata2 = str(metadata).replace('\'','')

        #print(metadata)
        sqlite_helper.update_db(real_path, json.dumps(metadata2), 'done', ex_ls, total_time)
        print("Database updated. ")

        metadata = json.dumps(metadata)
        metadata = json.loads(metadata)

        print(metadata)
        post_to_API(metadata)


def get_freetext_metadata(filename, old_mdata):

    t0 = time.time()
    metadata = extract_topic('file', filename)
    t1 = time.time()

    if 'ex_freetext' in old_mdata:
        print("There's already structured metadata for this file. ")
        return None  # Return nothing because no point.

    else:
        return (metadata, t1-t0)


def get_structured_metadata(filename, old_mdata):

    try:  # TODO: Are we updating ex_ls?
        with open(filename, 'rU') as file_handle:

            t0 = time.time()
            metadata = extract_columnar_metadata(file_handle)
            t1 = time.time()

            if 'ex_structured' in old_mdata:
                print("There's already structured metadata for this file. ")
                return None  # Return nothing because no point.

            else:
                return (metadata, t1-t0)

    except:  # If the metadata extraction utterly fails.
        print("Structured Extraction Failed. Terminating now. ")
        return None


def post_to_API(metadatablob):

    # TODO: Instead of posting to Suhail's API, just write back to the database.
    #post_req = requests.post('http://always.cs.uchicago.edu:8000/api/skluma/', json=metadatablob)


main(debug=True)
