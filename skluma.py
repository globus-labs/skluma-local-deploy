
"""
    This is the main runnable file for a local Skluma deployment.
    As of right now, this local version does NOT support file update daemon.
"""

import argparse
import json
import os
import multiprocessing
import sqlite3

from subprocess import call, Popen

# Step 1. Check to see if temp folder and SQLite database exists.
db_path = "tmp/skluma-db3.db"
tmp_path = os.getcwd() + "/tmp/"

parser = argparse.ArgumentParser()
parser.add_argument("config_path", help = "Path to Skluma configuration JSON. ")

args = parser.parse_args()

with open(args.config_path, 'r') as f:
    config_dict = json.load(f)

username = config_dict["username"]
crawlable_path = config_dict["extraction-path"]

if not os.path.isdir('tmp'):
    os.mkdir('tmp')

# Step 1a. If SQLite DB does not exist, create one.
if not os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        print("Using SQLite Version: " + str(sqlite3.version))

        print("Creating tables...")
        c = conn.cursor()
        c.execute('''CREATE TABLE files (path text, user_id text, metadata text, last_extractor text, done text, file_size real, file_id text, ex_ls text)''')
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(e)

# Step 3. Spin up and launch crawler.
# TODO: Switch back to pyLogger and not 'print'.
# --- Note: We use the crawlable directory as a mounted Docker volume.
print("Launching file system crawler at path " + crawlable_path + ".")
call(["sudo", "docker", "build", "-t", "posix_crawler", "extractors/crawler"])
docker_crawl_path = "CRAWL_PATH=" + crawlable_path
print(docker_crawl_path)
call(["sudo", "docker", "run", "--rm","-e", docker_crawl_path ,  "-e", "DB_PATH=" + tmp_path + "skluma-db3.db", "-P", "-t", "-v", crawlable_path + "/:" + crawlable_path, "-v", tmp_path + ":" + tmp_path, "posix_crawler"])

# Step 4. Spin up and launch file sampler.
print("Background launching file system crawler at path " + crawlable_path + ".")
call(["sudo", "docker", "build", "-t" , "file_sampler", "extractors/file_sampler"])
Popen(["sudo", "docker", "run", "--rm", "-e", "DB_PATH=" + tmp_path + "skluma-db3.db", "-P", "-t", "-v", crawlable_path + "/:" + crawlable_path, "-v", tmp_path + ":" + tmp_path, "file_sampler"])

# Step 5. Launch #-cores-1 universal samplers.
total_cores = multiprocessing.cpu_count()
print(total_cores)

# TODO: Move compressed files to /tmp, decompress them, process, then delete.
# Step 5a. When crawler spins down, launch another main.
# Step 5b. When sampler spins down, launch another main.
