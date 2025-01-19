import sqlite3


def init_db():
    con = sqlite3.connect("history.db")
    cur = con.cursor()
    table = cur.execute("SELECT name FROM sqlite_master WHERE name = 'data'")
    if table.fetchone() is None:
        cur.execute("CREATE TABLE data(info) UNIQUE info")
    return con,cur

con, cur = init_db()

res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchone())

# cur.execute(""" INSERT INTO data VALUES ('LOLOLlOL') """)
# con.commit()

# res = cur.execute("SELECT info FROM data")
# print(res.fetchall())

# cur.execute("DELETE FROM data where info = 'LOLOLOL'")


# res = cur.execute("SELECT info FROM data")
# print(res.fetchall())
# cur.execute(""" DROP TABLE data """)
# res = cur.execute("SELECT name FROM sqlite_master")
# print(res.fetchone())

