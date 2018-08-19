import sqlite3

conn = sqlite3.connect('tmp/skluma-db3.db')

c = conn.cursor()


def count_rows():
    for row in c.execute("SELECT path, metadata FROM files;"): #WHERE last_extractor = 'main1';"):
        print(row)


def set_init():
    c.execute(""" UPDATE files SET last_extractor = 'init'; """)


count_rows()

conn.commit()
conn.close()

