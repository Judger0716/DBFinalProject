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
                            Balance double(10,2) default 0,
                            BorrowNum int(4) default 0,
                            Level smallint default 0
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
sql='''create table borrow ( 
                            BookId int(4),
                            Uid int(4),
                            StartDate date not null,
                            EndDate date not null,
                            isExpired bool default false,
                            isCalculated bool default false,
                            primary key (Uid, BookId),
                            foreign key (Uid) references Users(Uid),
                            foreign key (BookId) references Books(BookId)
                            )'''
cursor.execute(sql)
sql='''create table buy ( 
                            BookId int(4),
                            Uid int(4),
                            BuyDate date not null,
                            Price double(10,2) not null,
                            primary key (Uid, BookId),
                            foreign key (Uid) references Users(Uid),
                            foreign key (BookId) references Books(BookId)
                            )'''
cursor.execute(sql)
sql='''create table comment ( 
                            Cid int(8) primary key auto_increment,
                            Uid int(4),
                            BookId int(4),
                            Content varchar(200) not null,
                            CDate date not null,
                            foreign key (Uid) references Users(Uid),
                            foreign key (BookId) references Books(BookId)
                            )'''
cursor.execute(sql)

cursor.execute("SHOW TABLES")
for x in cursor:
    print(x)
