import sqlite3
DB = r"C:\Users\jlchz\OneDrive\Desktop\fincas\finca_ganadera.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
print('DB:', DB)
for row in cur.execute("PRAGMA table_info('empleado')"):
    print(row)
conn.close()
