"""
 @Author: 西琳
 @FileName: init_db.py
 @DateTime: 2024/7/29 下午7:34
 @SoftWare: PyCharm
"""
import pymysql

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    db='db',
    cursorclass=pymysql.cursors.DictCursor
)
try:
    with open('db.sql') as f:
        sql_commands = f.read().split(';')
        with conn.cursor() as cursor:
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
                        ('学习Flask1', '跟麦叔学习flask第一部分'))
            cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
                        ('学习Flask2', '跟麦叔学习flask第二部分'))
        conn.commit()
finally:
    conn.close()
