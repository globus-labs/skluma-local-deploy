
import os
import sqlite3

DB_PATH = os.environ["DB_PATH"]

def get_next_file():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = """SELECT path, metadata, last_extractor FROM files WHERE last_extractor <> 'init' AND last_extractor <> 'main1' LIMIT 1; """

    cur.execute(query)
    conn.commit()
    results = cur.fetchall()

    unsampled_files = []
    for hit in results:
        unsampled_files.append(hit)

    return unsampled_files


def update_db(file_id, new_meta, next_extractor):
    """
    Function to update the database with the next extractor in the queue.
        :param str file_id -- id of the file to be updated in db.
        :param json new_meta -- the metadata to add to file's metadata field in db.
        :param str next_extractor -- the next extractor a file needs.
    """

    new_meta = get_postgres_str(str(new_meta).replace('\'', '\"'))

    conn3 = sqlite3.connect(DB_PATH)
    cur3 = conn3.cursor()

    data_query = """UPDATE files SET last_extractor = {}, metadata = {} WHERE path = {};"""
    data_query = data_query.format(get_postgres_str(next_extractor), new_meta, get_postgres_str(file_id))

    cur3.execute(data_query)

    conn3.commit()
    conn3.close()


def get_postgres_str(obj):
    """ Short helper method to add the apostrophes that postgres wants. Also casts to str. """
    string = "'" + str(obj) + "'"
    return string
