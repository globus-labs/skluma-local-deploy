import sqlite3

conn=sqlite3.connect('tmp/skluma-db3.db')

c = conn.cursor()


def count_rows():
    for row in c.execute("SELECT COUNT(*) FROM files"):
        print(row)

def set_init():
    print("hey.")



conn.commit()
conn.close()

