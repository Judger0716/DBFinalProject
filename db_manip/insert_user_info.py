import mysql.connector
import hashlib
import random

#建立数据库连接及表
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="bms"
)
cursor = mydb.cursor()


#插入管理员
username='admin'
password='admin'
hash = hashlib.md5()  #创建md5()加密实例
hash.update(bytes(username+password, encoding='utf-8')) 
print(str(hash.hexdigest())) 
sql=("insert into users (username,password,level) values ('%s', '%s', 1)" % (username, str(hash.hexdigest())))
cursor.execute(sql)
print(sql)


#获得用户输入并插入表中，admin:admin
print("Please input the user's information:")
username=input("username:")
passwd=input("passwd:")
balance=random.uniform(100,1000)
hash = hashlib.md5()  #创建md5()加密实例
hash.update(bytes(username+passwd, encoding='utf-8')) 
print(str(hash.hexdigest())) 
sql=("insert into users (username,password,balance,level) values ('%s', '%s', %f, 0)" % (username, str(hash.hexdigest()),balance))
cursor.execute(sql)
print(sql)
mydb.commit()
mydb.close()