

# TODO by end of day -- repeat this process for SQLite as we did for Postgres.

import json
import os
import sqlite3

# DB_PATH = os.environ["DB_PATH"]
DB_PATH = '/home/skluzacek/skluma-local-deploy/tmp/skluma-db3.db'


def get_next_file():

    #TODO: Make this get next file.

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # TODO: <> init; is not good enough...
    query = """SELECT path, metadata, last_extractor FROM files WHERE last_extractor <> 'init' AND last_extractor <> 'main' LIMIT 1; """

    cur.execute(query)
    conn.commit()
    results = cur.fetchall()

    unsampled_files = []
    for hit in results: 
        print(hit)

    return unsampled_files


def update_db(file_id, new_meta, next_extractor, ext_list, time_taken):
    ''' Function to update the database with the next extractor in the queue.
        :param str file_id -- id of the file to be updated in db.
        :param json new_meta -- the metadata to add to file's metadata field in db.
        :param str next_extractor -- the next extractor a file needs.
        :param list ext_list -- all of the extractors that a file has been processed with.
    '''

    new_meta = json.dumps(new_meta)

    conn3 = "hi"  # TODO DB Connection.

    cur3 = conn3.cursor()

    #TODO: Done = 'T' is VERY important and should be used to avoid pulling the top file 1000 times.
    #TODO: TYLER -- start by getting this query to work. :) 3:16pm.

    data_query = """UPDATE files2 SET last_extractor = {0}, metadata = {1}, done = 't', ex_ls={2}, totaltime={4} WHERE path = {3};"""
    data_query = data_query.format(get_postgres_str(next_extractor), get_postgres_str(new_meta),
                                   get_postgres_str(str(ext_list).replace('\'', '"')), get_postgres_str(file_id),
                                   time_taken)
    cur3.execute(data_query)

    conn3.commit()
    conn3.close()

def get_postgres_str(obj):
    """ Short helper method to add the apostrophes that postgres wants. Also casts to str. """
    string = "'" + str(obj) + "'"
    return string

get_next_file()