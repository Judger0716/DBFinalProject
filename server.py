from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
import mysql.connector
import hashlib
import datetime

app = Flask(__name__)

# 首页为登录界面
@app.route('/', methods=['GET'])
def signin_form():
    return render_template('login.html')


# GET /login 同首页
@app.route('/login',methods=['GET'])
def sigin_interface():
    return render_template('login.html',msg='请输入用户名和密码登录')


# POST /login 尝试登录
@app.route('/login', methods=['POST'])
def signin():

    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="guest",
        passwd="guest",
        database="bms"
    )
    cursor = mydb.cursor()
    # 获得当前用户名对应的密码
    sql=('''
        select password,level
        from users
        where username='%s'
        ''' % (request.form['username']))
    cursor.execute(sql)
    print(sql)
    values=cursor.fetchall()
    # 如果无此用户，则返回错误
    if(len(values)==0):
        mydb.commit()
        mydb.close()
        return render_template('login.html',msg='无此用户')
    user_class=values[0][1]
    # 管理员用户
    if(user_class==1):
        mydb.commit()
        mydb.close()
        return render_template('admin.html')
    # 判断密码是否正确
    current_passwd=values[0][0]
    hash = hashlib.md5()  #创建md5()加密实例
    hash.update(bytes(request.form['username']+request.form['password'], encoding='utf-8'))
    input_passwd=str(hash.hexdigest())
    if input_passwd==current_passwd:
        mydb.commit()
        mydb.close()
        return redirect(url_for('get_book',username=request.form['username']))
    mydb.commit()
    mydb.close()
    return render_template('login.html',msg='用户名或密码不正确')


# GET /regist 获得注册页面
@app.route('/regist',methods=['GET'])
def regist_form():
    return render_template('regist.html')


# POST /regist 注册用户
@app.route('/regist', methods=['POST'])
def regist():
    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="bms"
    )
    cursor = mydb.cursor()
    hash = hashlib.md5()  #创建md5()加密实例
    hash.update(bytes(request.form['username']+request.form['password'], encoding='utf-8'))
    # 插入数据
    sql=('''
        insert into users (username, password)
        values ('%s','%s')
        ''' % (request.form['username'], str(hash.hexdigest())))
    try:
        cursor.execute(sql)
        mydb.commit()
        mydb.close()
        return render_template('login.html',msg='注册成功')
    except:
        mydb.commit()
        mydb.close()
        return render_template('login.html',msg='注册失败')

# POST /chginfo 修改已注册的用户信息
@app.route('/chginfo', methods=['POST'])
def change_info():
    response_object = {'status': 'success'}
    post_data=request.get_json()
    before_username=post_data.get('before_username')
    before_password=post_data.get('before_password')
    after_username=post_data.get('after_username')
    after_password=post_data.get('after_password')
    print(before_username,before_password,after_username,after_password)
    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="bms"
    )
    cursor = mydb.cursor()
    # 获得当前用户名对应的密码
    sql='''
        select password,uid
        from users
        where username like '{un}'
        '''.format(un=before_username)
    cursor.execute(sql)
    print(sql)
    values=cursor.fetchall()
    print(values)
    current_uid=values[0][1]
    # 判断密码是否正确
    current_passwd=values[0][0]
    hash = hashlib.md5()  #创建md5()加密实例
    hash.update(bytes(before_username+before_password, encoding='utf-8'))
    input_passwd=str(hash.hexdigest())
    if input_passwd==current_passwd:
        hash = hashlib.md5()  #创建md5()加密实例
        hash.update(bytes(after_username+after_password, encoding='utf-8'))
        new_passwd=str(hash.hexdigest())
        sql='''
            update users
            set username='{newun}', password='{newpasswd}'
            where uid={curid}
            '''.format(newun=after_username,newpasswd=new_passwd,curid=current_uid)
        try:
            cursor.execute(sql)
            print(sql)
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='duplicated_username'
            return jsonify(response_object)
    else:
        mydb.commit()
        mydb.close()
        response_object['status']='incorrect_password'
        return jsonify(response_object)


# GET /book 获得图书管理主界面
@app.route('/book/?<string:username>', methods=['GET'])
def get_book(username):
    return render_template('book.html',username=username)


# POST /book 查询图书信息
@app.route('/book', methods=['POST'])
def search_book():
    BOOKS=[]
    response_object = {'status': 'success'}
    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="bms"
    )
    cursor = mydb.cursor()
    # 获得书名、作者、出版社信息
    post_data=request.get_json()
    bookname=post_data.get('bookname')
    author=post_data.get('author')
    publisher=post_data.get('publisher')
    # 构造sql语句
    sql='''
        select * from books
        where bookname like '%{bn}%'
        and author like '%{athr}%'
        and publisher like '%{pblshr}%'
        '''.format(bn=bookname,athr=author,pblshr=publisher)
    print(sql)
    try:
        cursor.execute(sql)
        sch_result=cursor.fetchall()
        for i in range(len(sch_result)):
            BOOKS.append({
                'bookid': sch_result[i][0],
                'bookname': sch_result[i][1],
                'author': sch_result[i][2], 
                'publisher': sch_result[i][3],
                'publishdate': sch_result[i][4],
                'price': sch_result[i][5],
                'storage': sch_result[i][6],
            })
        mydb.commit()
        mydb.close()
        response_object['books']=BOOKS
        return jsonify(response_object)
    except:
        print('select error!')
        response_object['status']='failed'
        return jsonify(response_object)


# POST /borrow 借阅书籍
@app.route('/borrow', methods=['POST'])
def borrow_book():
    response_object = {'status': 'borrow_successfully'}
    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="bms"
    )
    cursor = mydb.cursor()
    post_data = request.get_json()
    message = post_data.get('message')

    # 申请借阅，检查库存
    if(message=='request_borrow'):
        username = post_data.get('username')
        bookid = post_data.get('bookid')
        # 检查该用户的已借阅数目
        sql='''
            select borrownum from users
            where username like '{un}'
            '''.format(un=username)
        cursor.execute(sql)
        borrow_num=cursor.fetchone()[0]
        # 以及达到上限，拒绝借阅
        if(borrow_num==10):
            response_object['status']='maximum_borrow_num'
            mydb.commit()
            mydb.close()
            return jsonify(response_object)

        sql='''
            select storage from books
            where bookid={bi}
            '''.format(bi=bookid)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchone()
            storage=sch_result[0]
            mydb.commit()
            mydb.close()
            # 如果库存为0，则不允许借阅
            if(storage==0):
                response_object['status']='no_storage'
                return jsonify(response_object)
            else:
                # 否则告知客户端可以借阅，选择借阅日期
                response_object['status']='accept'
                return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='borrow_failed'
            return jsonify(response_object)

    # 确认借阅，用户给出借阅书号
    elif(message=='commit_borrow'):
        # 获得书号、用户名、起止日期
        bookid = post_data.get('bookid')
        username=post_data.get('username')
        startdate=post_data.get('startdate')[:10]
        enddate=post_data.get('enddate')[:10]

        # 更新用户的信誉分，存储过程实现
        sql='''
            select borrow.bookid,borrow.uid,enddate,iscalculated
            from borrow,users
            where borrow.uid=users.uid and users.username='{un}'
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        details=cursor.fetchall()
        if(len(details)>0):
            now=datetime.date.today() # 当前时间
            minus=0 # 扣除的信誉分
            for i in range(len(details)):
                # 未统计过的逾期
                if(details[i][2]<now and details[i][3]==False):
                    minus=minus+10
                    sql='''
                        update borrow
                        set isexpired=true,iscalculated=true
                        where bookid={bi} and uid={ui}
                        '''.format(bi=details[i][0],ui=details[i][1])
                    cursor.execute(sql)
            # 扣除信誉分
            sql='''
                update users
                set credit=credit-{m}
                where uid={ui}
                '''.format(m=minus,ui=details[0][1])
            cursor.execute(sql)
            mydb.commit()

        # 获取信誉分
        sql='''
            select uid, credit from users where username like '{un}'
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchall()
        uid=data[0][0]
        credit=data[0][1]
        response_object['credit']=credit
        
        # 信誉分低于60，拒绝借阅
        if(credit<60):
            print("LOW CREDIT")
            response_object['status']='low_credit'
            return jsonify(response_object)
        
        # 重复借阅，拒绝
        sql='''
            select bookid from borrow 
            where bookid={_bookid} and uid={_uid}
            '''.format(_uid=uid,_bookid=bookid)
        cursor.execute(sql)
        print(sql)
        if(len(cursor.fetchall())>0):
            response_object['status']='already_borrowed'
            return jsonify(response_object)

        # 添加借阅记录，更新库存以及书的已阅读字段
        sql='''
            insert into borrow 
            values ({_bookid},{_uid},'{sd}','{ed}',false,false)
            '''.format(_bookid=bookid,_uid=uid,sd=startdate,ed=enddate)
        try:
            cursor.execute(sql)
            print(sql)
            # 更新书籍的库存，阅读量
            sql='''
                update books
                set storage=storage-1, readed=readed+1
                where bookid={_bookid}
                '''.format(_bookid=bookid)
            cursor.execute(sql)
            print(sql)
            # 更新用户的借阅数量
            sql='''
                update users
                set borrownum=borrownum+1
                where uid={_uid}
                '''.format(_uid=uid)
            cursor.execute(sql)
            print(sql)
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            response_object['status']='borrow_failed'
            return jsonify(response_object)
    
    # 查看用户的借阅记录
    elif(message=='get_borrow_list'):
        BORROW_LIST=[]
        username=post_data.get('username')

        # 更新用户的信誉分，存储过程实现
        sql='''
            select borrow.bookid,borrow.uid,enddate,iscalculated
            from borrow,users
            where borrow.uid=users.uid and users.username='{un}'
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        details=cursor.fetchall()
        if(len(details)>0):
            now=datetime.date.today() # 当前时间
            minus=0 # 扣除的信誉分
            for i in range(len(details)):
                # 未统计过的逾期
                if(details[i][2]<now and details[i][3]==False):
                    minus=minus+10
                    sql='''
                        update borrow
                        set isexpired=true,iscalculated=true
                        where bookid={bi} and uid={ui}
                        '''.format(bi=details[i][0],ui=details[i][1])
                    cursor.execute(sql)
            # 扣除信誉分
            sql='''
                update users
                set credit=credit-{m}
                where uid={ui}
                '''.format(m=minus,ui=details[0][1])
            cursor.execute(sql)

        # 获取信誉分
        sql='''
            select credit from users where username like '{un}'
            '''.format(un=username)
        cursor.execute(sql)
        data=cursor.fetchall()
        credit=data[0][0]
        response_object['credit']=credit

        sql='''
            select borrow.bookid, books.bookname, startdate, enddate, isexpired
            from borrow, books
            where borrow.bookid=books.bookid and borrow.uid in (
                select uid from users where username like '{un}'
            )
            '''.format(un=username)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                BORROW_LIST.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'startdate': sch_result[i][2], 
                    'enddate': sch_result[i][3],
                    'isexpired': sch_result[i][4],
                })
            mydb.commit()
            mydb.close()
            response_object['bl']=BORROW_LIST
            response_object['status']='get_borrow_list_successfully'
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='get_borrow_list_failed'
            return jsonify(response_object)

    # 取消借阅
    elif(message=='recall_borrow'):
        username=post_data.get('username')
        bookid=post_data.get('bookid')
        # 如果有这条记录，则删除
        sql='''
            select * from borrow
            where bookid={bi} 
            and uid in (select uid from users where username like '{un}')
            '''.format(bi=bookid,un=username)
        cursor.execute(sql)
        if(len(cursor.fetchall())>0):
            sql='''
                delete from borrow
                where bookid={bi} 
                and uid in (select uid from users where username like '{un}')
                '''.format(bi=bookid,un=username)
            cursor.execute(sql)
            print(sql)
            # 减少信誉分
            sql='''
                update users
                set credit=credit-10
                where username like '{un}'
                '''.format(un=username)
            cursor.execute(sql)
            print(sql)
            # 减少阅读量,库存增加
            sql='''
                update books
                set readed=readed-1,storage=storage+1
                where bookid={bi}
                '''.format(bi=bookid)
            cursor.execute(sql)
            print(sql)
            mydb.commit()
            mydb.close()
            response_object['status']='recall_successfully'
            return jsonify(response_object)
        else:
            response_object['status']='recall_failed'
            return jsonify(response_object)

if __name__ == '__main__':
    app.run()