import sqlite3

conn=sqlite3.connect('tmp/skluma-db3.db')

c = conn.cursor()

for row in c.execute("SELECT * FROM files"):
    print(row)

conn.commit()

conn.close()

