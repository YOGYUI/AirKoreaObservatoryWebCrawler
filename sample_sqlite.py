import sqlite3

dbpath = './airkorea_obs_list.db'
conn = sqlite3.connect(dbpath)
cursor = conn.cursor()
sql = "SELECT * FROM airkoreaobs LIMIT 10;"
cursor.execute(sql)
records = cursor.fetchall()
for elem in records:
    print(elem)

sql = "SELECT * FROM airkoreaobs;"
cursor.execute(sql)
records = cursor.fetchall()
print(f"총 레코드 개수: {len(records)}")
conn.close()
