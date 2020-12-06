import mysql.connector
import hashlib

#建立数据库连接及表
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="bms"
)
cursor = mydb.cursor()

#获得用户输入并插入表中
print("Please input the user's information:")
username=input("username:")
passwd=input("passwd:")
hash = hashlib.md5()  #创建md5()加密实例
hash.update(bytes(username+passwd, encoding='utf-8')) 
print(str(hash.hexdigest())) 
sql=("insert into users (username,password) values ('%s', '%s')" % (username, str(hash.hexdigest())))
print(sql)
cursor.execute(sql)
print(cursor.rowcount, "条记录已插入")
mydb.commit()