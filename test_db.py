import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="bms"
)
cursor = mydb.cursor()
sql='''
            select borrow.bookid, books.bookname, startdate, enddate, isexpired
            from borrow, books
            where borrow.bookid=books.bookid and borrow.uid in (
                select uid from users where username like '{un}'
            )
            '''.format(un='zhangyanran')
cursor.execute(sql)
print(sql)
print(cursor.fetchall())
mydb.commit()
mydb.close()