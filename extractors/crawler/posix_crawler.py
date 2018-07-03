

"""
    This ftp/local-directory_scraper will create a path-directory of all files and filesizes in given FTP server.
    Code can be uncommented to (1) do in a single recursive swath, and (2) actually download files
    a local machine. It implements Depth-First Search (DFS).
    
        @Author: Tyler J. Skluzacek, University of Chicago
        @Email: skluzacek@uchicago.edu
        @Github: tskluzac
        @LastEdited: 07/03/2018
"""

import json
import os
import sqlite3

DB_PATH = os.environ["DB_PATH"]

# A couple of global variables used for sanity checks across recursive functions. Change in meaning for debugging.
CLOUD_REPO = False
COUNT = 0


def increment():
    '''Increments the global COUNT variable. Used for debugging. '''
    global COUNT
    COUNT = COUNT + 1
    return COUNT


class PostgresConnectException(Exception):
    """Throw this when we cannot connect to Postgres in RDS. """

ftp = None

def _is_ftp_dir(ftp_handle, name, guess_by_extension=True):
    """ Test to see if we are in an ftp directory
        :param ftp_handle -- our link to the ftp directory connection
        :param name -- file name
        :param guest_by_extension
    """

    if guess_by_extension is True:
        if (name[-4] == '.') or (name[-3] == '.') or (name[-2] == '.'):
            return False

    original_cwd = ftp_handle.pwd()     # Current Working Directory
    try:
        ftp_handle.cwd(name)            # see if name represents a child-subdirectory
        ftp_handle.cwd(original_cwd)    # It works! Go back. Continue DFS.
        return True
    except:
        return False


def _make_parent_dir(fpath):
    """ Does path (given a file) actually exist?
        :param fpath -- path to the file. """
    dirname = os.path.dirname(fpath)
    while not os.path.exists(dirname):
        try:
            os.mkdir(dirname)
        except:
            _make_parent_dir(dirname)


def _download_ftp_file(ftp_handle, name, dest, overwrite, path_size_holder):
    """ Unpack each file's size. """
    size = ftp.size(name)
    path_size_tuple = (name, size)

    # Write the file to the database.
    file_id = rename_file("skluzacek@uchicago.edu", name)

    if dup_check(file_id) == True:
        write_to_postgres(path_size_tuple)
        pass
    else:
        pass


def _mirror_ftp_dir(ftp_handle, name, overwrite, guess_by_extension, path_size_holder):
    """ replicates a directory on an ftp server recursively """
    for item in ftp_handle.nlst(name):
        if _is_ftp_dir(ftp_handle, item):
            _mirror_ftp_dir(ftp_handle, item, overwrite, guess_by_extension, path_size_holder)
        else:
            _download_ftp_file(ftp_handle, item, item, overwrite, path_size_holder)


def download_ftp_tree(ftp_handle, path, overwrite=False, guess_by_extension=True):
    """
    Downloads an entire directory tree from an ftp server to the local destination
    :param ftp_handle: an authenticated ftplib.FTP instance
    :param path: the folder on the ftp server to download
    :param destination: the local directory to store the copied folder
    :param overwrite: set to True to force re-download of all files, even if they appear to exist already
    :param guess_by_extension: It takes a while to explicitly check if every item is a directory or a file.
        if this flag is set to True, it will assume any file ending with a three character extension ".???" is
        a file and not a directory. Set to False if some folders may have a "." in their names -4th position.
    """
    path_size_holder = [('Path', 'Size')]
    _mirror_ftp_dir(ftp_handle, path, overwrite, guess_by_extension, path_size_holder)


def is_compressed(filename):
    filename = filename.lower()
    zips = ["zip", "tar", "z", "gz"]
    return filename, zips


# TODO: [TYLER] Local deployment complicates this. Will return to this.
def dup_check(file_id):
    return True


def write_to_postgres(info_tuple):
    """ Take a tuple containing path and file-size, and update the table with this information.  This should also
        inform the user that they. """

    count = increment()

    if count % 1000 == 0:
        print("Files processed thus far: " + str(count))

    # Postgres annoyingly needs single-quotes on everything
    path = '\'' + info_tuple[0] + '\''
    size = info_tuple[1]
    meta_empty = '\'' + json.dumps({}) + '\''
    cont1 = "'init'"
    done = "'True'"

    # TODO: Generalize into config.
    file_id = '\'' + rename_file("skluzacek@uchicago.edu", info_tuple[0]) + '\''

    try:
        conn = sqlite3.connect(DB_PATH)
    except:
        print("Unable to connect to SQLite...")

    query = """INSERT INTO files (path, user_id, metadata, last_extractor, done, file_size, file_id, ex_ls) VALUES ({0}, 123456, {1}, {2}, {3}, {4}, {5}, {6});"""
    query = query.format(str(path), str(meta_empty), str(cont1), str(done), int(size), str(file_id), get_postgres_str([]))  # TODO: Relax 123456 to fit any user.

    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()
    # print("Successfully wrote file with path " + path + " to DB. ")
    return True


# TODO: Find a means for subdividing the repository for faster DFS.
def rename_file(useremail, filepath):
    try:
        os.chdir("../../tmp")  # TODO: I don't think I need this here.
    except:
        pass

    file_list = filepath

    if '/' in file_list:
        file_list = filepath.split('/')

    elif '\\' in file_list:
        file_list = filepath.split('\\')

    use_rmash = ('-'.join(useremail.split('@'))).replace('.','')
    file_mash = ''.join(file_list)
    new_name = use_rmash + '-' + file_mash

    return new_name


def get_metadata(directory):
    """Crawl local filesystem. Return state (i.e, file list)
        :param directory string representing root level directory path """
    pass
    r = []
    subdirs = [x[0] for x in os.walk(directory)]
    for subdir in subdirs:
        files = os.walk(subdir).__next__()[2]
        if len(files) > 0:
            for item in files:
                file_path = subdir + "/" + item
                size = os.stat(file_path).st_size
                try:
                    write_to_postgres((file_path, size))
                except sqlite3.OperationalError as e:
                    print("Bad file format... Passing: " + str(e))
    return r


def get_postgres_str(obj):
    """ Short helper method to add the apostrophes that postgres wants. Also casts to str. """
    string = "'" + str(obj) + "'"
    return string


def launch_crawler(repo_path):

    directory_input = repo_path

    if not CLOUD_REPO:
        print("Getting Metadata for Files.")
        get_metadata(directory_input)

    else:
        raise FileNotFoundError("Unable to connect to remote host. LOCAL DEPLOYMENT. ")

    exit()


launch_crawler(os.environ["CRAWL_PATH"])
