import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="bms"
)
cursor = mydb.cursor()

sql='''create table users ( 
                            Uid int(4) primary key auto_increment,
                            Username varchar(40) unique not null,
                            Password varchar(40) not null,
                            Credit int(4) default 100,
                            BorrowNum int(4) default 0,
                            AptNum int(4) default 0
                            )'''
cursor.execute(sql)
sql='''create table books ( 
                            BookId int(4) primary key auto_increment,
                            BookName varchar(50) unique not null,
                            Author varchar(30) not null,
                            Publisher varchar(40),
                            PublishDate date,
                            Price double(10,2) not null,
                            Storage int(4),
                            Readed int(4) default 0,
                            Purchased int(4) default 0
                            )'''
cursor.execute(sql)


cursor.execute("SHOW TABLES")
for x in cursor:
    print(x)
