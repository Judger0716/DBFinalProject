import numpy as py
import pandas as pd
import random
import xlrd
import mysql.connector

#建立数据库连接
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="bms"
)
cursor = mydb.cursor()

df=pd.read_excel('db_manip/bookinfo.xlsx')
book_sum=len(df.index.values)
success=0
error=0
for i in range(book_sum):
    data=df.loc[i].values
    book_name=data[0]
    author=data[1]
    publisher=data[2]
    publish_date=data[3]
    intro=data[4]
    try:
        price=float(data[5][1:])
        comment=data[6]
        storage=random.randint(1,10)
        sql=('''insert into books (bookname, author, publisher, publishdate, price, storage)
                values ('%s','%s','%s','%s',%f,%d)''' % (book_name, author, publisher, publish_date, price, storage) )
        try:
            cursor.execute(sql)
            success+=1
        except:
            error+=1
    except:
        continue


print("Successfully added %d books, %d books ERROR" % (success, error))
mydb.commit()
mydb.close()