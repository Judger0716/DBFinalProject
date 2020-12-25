from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
import mysql.connector
import hashlib
import datetime
import time

app = Flask(__name__)

# 防止SQL注入过滤器
def isValid(sql):
    init_len=len(sql)
    if(init_len==0):
        return False
    dirty_stuff = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "<", ">", "+", "%", "$", "(", ")", "%", "@","!"]
    for stuff in dirty_stuff:
        sql = sql.replace(stuff, "")
    final_len=len(sql)
    if(init_len==final_len):
        return True
    else:
        return False

# 首页为登录界面
@app.route('/', methods=['GET'])
def signin_form():
    return render_template('login.html')


# GET /login 同首页
@app.route('/login',methods=['GET'])
def sigin_interface():
    return render_template('login.html',msg='提示：请输入用户名和密码登录')


# POST /login 尝试登录
@app.route('/login', methods=['POST'])
def signin():

    # 连接数据库，只需使用guest
    mydb = mysql.connector.connect(
        host="localhost",
        user="guest",
        passwd="guest",
        database="bms"
    )
    cursor = mydb.cursor()

    # 获得当前用户名对应的密码，使用S锁，当用户修改用户名和密码时，不能使用原用户名和密码登录
    if(isValid(request.form['username'])):
        sql=('''
        select password,level
        from users
        where username='%s'
        lock in share mode
        ''' % (request.form['username']))
        cursor.execute(sql)
        print(sql)
    else:
        return render_template('login.html',msg='提示：用户名或密码不正确')
    values=cursor.fetchall()

    # 如果无此用户，则返回错误
    if(len(values)==0):
        mydb.commit()
        mydb.close()
        return render_template('login.html',msg='提示：无此用户')
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
    return render_template('login.html',msg='提示：用户名或密码不正确')


# GET /regist 获得注册页面
@app.route('/regist',methods=['GET'])
def regist_form():
    return render_template('regist.html')


# POST /regist 注册用户
@app.route('/regist', methods=['POST'])
def regist():
    if(isValid(request.form['username']) and isValid(request.form['password'])):
        if(len(request.form['password'])<6):
            return render_template('login.html',msg='注册失败，密码过短')
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
        try:
            # 插入用户
            cursor.callproc('add_usr',(request.form['username'],str(hash.hexdigest())))
            print("callproc add_usr")
            mydb.commit()
            mydb.close()
            return render_template('login.html',msg='注册成功')
        except:
            mydb.commit()
            mydb.close()
            return render_template('login.html',msg='注册失败')
    else:
        return render_template('login.html',msg='注册失败')

# POST /getinfo 查看已注册的用户信息
@app.route('/getinfo', methods=['POST'])
def get_info(): 
    response_object = {'status': 'success'}
    post_data=request.get_json()
    username=post_data.get('username')

    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="guest",
        passwd="guest",
        database="bms"
    )
    cursor = mydb.cursor()

    # 获得当前用户信息，如果用户信息正在被修改，则应该得到修改后的信息
    sql='''
        select * from users
        where username like '{un}'
        lock in share mode
        '''.format(un=username)
    try:
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchone()
        userinfo={}
        userinfo['uid']=data[0]
        userinfo['username']=data[1]
        userinfo['credit']=data[3]
        userinfo['balance']=data[4]
        userinfo['borrownum']=data[5]
        userinfo['level']=data[6]
        response_object['userinfo']=userinfo
        mydb.commit()
        mydb.close()
        return jsonify(response_object)
    except:
        mydb.commit()
        mydb.close()
        response_object['status']='failed'
        return jsonify(response_object)

# POST /chginfo 修改已注册的用户信息
@app.route('/chginfo', methods=['POST'])
def change_info():
    response_object = {'status': 'success'}
    post_data=request.get_json()
    before_username=post_data.get('before_username')
    before_password=post_data.get('before_password')
    after_username=post_data.get('after_username')
    after_password=post_data.get('after_password')

    # 修改后的用户名和密码含有非法字符或密码长度小于6
    if(not isValid(after_username) or not isValid(after_password) or len(after_password)<6):
        response_object['status']='invalid_info'
        return jsonify(response_object)

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
        lock in share mode
        '''.format(un=before_username)
    cursor.execute(sql)
    print(sql)
    values=cursor.fetchall()
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
        try:
            # 合法，更新用户和密码
            cursor.callproc('chg_passwd',(after_username,new_passwd,current_uid))
            print("callproc chg_passwd")
            #time.sleep(20)  # 测试锁
            #print('awaken')
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            # 不合法，用户名重复
            mydb.commit()
            mydb.close()
            response_object['status']='duplicated_username'
            return jsonify(response_object)
    else:
        # 输入原有密码有误
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
    # 连接数据库，查询只需要使用guest
    mydb = mysql.connector.connect(
        host="localhost",
        user="guest",
        passwd="guest",
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
    try:
        cursor.execute(sql)
        print(sql)
        sch_result=cursor.fetchall()
        for i in range(len(sch_result)):
            BOOKS.append({
                'bookid': sch_result[i][0],
                'bookname': sch_result[i][1],
                'author': sch_result[i][2], 
                'publisher': sch_result[i][3],
                'publishdate': str(sch_result[i][4]),
                'price': sch_result[i][5],
                'storage': sch_result[i][6],
            })
        mydb.commit()
        mydb.close()
        response_object['books']=BOOKS
        return jsonify(response_object)
    except:
        mydb.commit()
        mydb.close()
        response_object['status']='failed'
        return jsonify(response_object)


# POST /borrow 借阅书籍
@app.route('/borrow', methods=['POST'])
def borrow_book():
    response_object = {'status': 'borrow_successfully'}
    post_data = request.get_json()
    message = post_data.get('message')

    # 申请借阅，检查库存
    if(message=='request_borrow'):
        # 申请借阅，不修改数据库，使用guest
        mydb = mysql.connector.connect(
            host="localhost",
            user="guest",
            passwd="guest",
            database="bms"
        )
        cursor = mydb.cursor()
        username = post_data.get('username')
        bookid = post_data.get('bookid')
        # 检查该用户的已借阅数目,如果用户正在还书，则应读取还书之后的数据
        sql='''
            select borrownum from users
            where username like '{un}'
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        borrow_num=cursor.fetchone()[0]
        # 以及达到上限，拒绝借阅
        if(borrow_num==10):
            response_object['status']='maximum_borrow_num'
            mydb.commit()
            mydb.close()
            return jsonify(response_object)

        # 如果有其他用户还书，应当读取到还书后的库存
        sql='''
            select storage from books
            where bookid={bi}
            lock in share mode
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
        # 添加借阅记录，使用root
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="bms"
        )
        cursor = mydb.cursor()
        # 获得书号、用户名、起止日期
        bookid = post_data.get('bookid')
        username=post_data.get('username')
        startdate=post_data.get('startdate')[:10]
        enddate=post_data.get('enddate')[:10]
        now=datetime.date.today()

        # 更新用户的信誉分，存储过程实现
        sql='''
            select borrow.bookid,borrow.uid,enddate,iscalculated
            from borrow,users
            where borrow.uid=users.uid and users.username='{un}'
            and iscalculated=false
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        details=cursor.fetchall()
        if(len(details)>0):
            minus=0 # 扣除的信誉分
            for i in range(len(details)):
                # 未统计过的逾期
                if(details[i][2]<now and details[i][3]==False):
                    minus=minus+10
                    cursor.callproc('cal_expired',(details[i][0],details[i][1]))
                    print("callproc cal_expired")
                    mydb.commit()
            # 扣除信誉分
            cursor.callproc('minus_credit',(minus,details[0][1]))
            print("callproc minus_credit")
            mydb.commit()

        # 获取信誉分
        sql='''
            select uid, credit from users where username like '{un}'
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchall()
        uid=data[0][0]
        credit=data[0][1]
        response_object['credit']=credit
        
        # 信誉分低于60，拒绝借阅
        if(credit<60):
            response_object['status']='low_credit'
            return jsonify(response_object)
        
        # 重复借阅，拒绝
        sql='''
            select bookid from borrow 
            where bookid={_bookid} and uid={_uid}
            lock in share mode
            '''.format(_uid=uid,_bookid=bookid)
        cursor.execute(sql)
        print(sql)
        if(len(cursor.fetchall())>0):
            response_object['status']='already_borrowed'
            return jsonify(response_object)

        # 添加借阅记录，更新库存以及书的已阅读字段，事务实现
        try:
            cursor.callproc('add_borrow',(bookid,uid,startdate,enddate))
            print("callproc add_borrow")
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.rollback()
            mydb.close()
            response_object['status']='borrow_failed'
            return jsonify(response_object)
    
    # 查看用户的借阅记录
    elif(message=='get_borrow_list'):
        # 获取借阅记录，更新用户的信誉分，使用root
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="bms"
        )
        cursor = mydb.cursor()
        BORROW_LIST=[]
        username=post_data.get('username')

        # 更新用户的信誉分，存储过程实现
        sql='''
            select borrow.bookid,borrow.uid,enddate,iscalculated
            from borrow,users
            where borrow.uid=users.uid and users.username='{un}'
            and iscalculated=false
            lock in share mode
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
                    cursor.callproc('cal_expired',(details[i][0],details[i][1]))
                    mydb.commit()
            # 扣除信誉分
            cursor.callproc('minus_credit',(minus,details[0][1]))
            mydb.commit()

        # 获取信誉分
        sql='''
            select credit from users where username like '{un}'
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        data=cursor.fetchall()
        credit=data[0][0]
        response_object['credit']=credit

        # 获取借阅列表，计算到期时间
        sql='''
            select borrow.bookid, books.bookname, startdate, enddate, isexpired, datediff(enddate,CURDATE()) remain
            from borrow, books
            where borrow.bookid=books.bookid and borrow.uid in (
                select uid from users where username like '{un}'
            )
            order by remain
            lock in share mode
            '''.format(un=username)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            now=datetime.date.today() # 当前时间
            for i in range(len(sch_result)):
                # 计算借阅是否已经开始
                if(now>=sch_result[i][2]):
                    isstarted=True
                else:
                    isstarted=False
                BORROW_LIST.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'startdate': str(sch_result[i][2]), 
                    'enddate': str(sch_result[i][3]),
                    'remain': sch_result[i][5],
                    'isstarted': isstarted,
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
        # 需要删除记录，使用root
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="bms"
        )
        cursor = mydb.cursor()
        username=post_data.get('username')
        bookid=post_data.get('bookid')
        # 如果有这条记录，则删除
        sql='''
            select * from borrow
            where bookid={bi} 
            and uid in (select uid from users where username like '{un}')
            lock in share mode
            '''.format(bi=bookid,un=username)
        cursor.execute(sql)
        if(len(cursor.fetchall())>0):
            # 删除未开始的借阅记录（是否开始由isstarted和isexpired共同决定），事务实现
            # 减少信誉分，已借阅数减少
            # 减少阅读量,库存增加
            try:
                cursor.callproc('recall_borrow',(bookid,username))
                print("callproc recall_borrow")
                mydb.commit()
                mydb.close()
                response_object['status']='recall_successfully'
                return jsonify(response_object)
            except:
                mydb.rollback()
                mydb.close()
                response_object['status']='recall_failed'
                return jsonify(response_object)
        else:
            response_object['status']='recall_failed'
            return jsonify(response_object)

# POST /buy 购买书籍
@app.route('/buy', methods=['POST'])
def buy_book():
    response_object = {'status': 'buy_successfully'}
    post_data = request.get_json()
    message = post_data.get('message')

    # 请求购买图书，检查库存
    if(message=='request_buy'):
        # 检查库存，使用guest
        mydb = mysql.connector.connect(
            host="localhost",
            user="guest",
            passwd="guest",
            database="bms"
        )
        cursor = mydb.cursor()
        bookid = post_data.get('bookid')
        username=post_data.get('username')
        
        sql='''
            select storage,bookname,price from books
            where bookid={bi}
            lock in share mode
            '''.format(bi=bookid)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            storage=sch_result[0][0]
            bookname=sch_result[0][1]
            price=sch_result[0][2]
            # 如果库存为0，则不允许购买
            if(storage==0):
                mydb.commit()
                mydb.close()
                response_object['status']='no_storage'
                return jsonify(response_object)
            else:
                # 否则告知客户端可以购买,更新前端信誉分
                sql='''
                    select credit from users
                    where username like '{un}'
                    lock in share mode
                    '''.format(un=username)
                cursor.execute(sql)
                credit=cursor.fetchone()[0]
                # 根据信誉分计算折扣discount
                discount=1.00-float(credit)/10000.0
                mydb.commit()
                mydb.close()
                response_object['discount']=round(discount,2)
                response_object['bookname']=bookname
                response_object['realprice']=round(price*discount,2)
                response_object['status']='accept'
                return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='buy_failed'
            return jsonify(response_object)

    elif(message=='commit_buy'):
        # 确认购买，添加购买记录，使用root
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="bms"
        )
        cursor = mydb.cursor()
        bookid=post_data.get('bookid')
        username=post_data.get('username')

        # 获取uid，账户余额以及信誉分
        sql='''
            select uid,balance,credit from users where username like '{un}'
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchall()
        uid=data[0][0]
        balance=data[0][1]
        credit=data[0][2]

        # 根据信誉分计算折扣discount
        discount=1.00-float(credit)/10000.0

        # 获取书价，并计算折扣后书价
        sql='''
            select price from books
            where bookid={bi}
            lock in share mode
            '''.format(bi=bookid)
        cursor.execute(sql)
        print(sql)
        price=cursor.fetchone()[0]
        final_price=price*discount

        # 余额不足(小于折后书价)，拒绝
        if(balance<final_price):
            response_object['status']='low_balance'
            return jsonify(response_object)
        
        # 重复购买，拒绝
        sql='''
            select bookid from buy
            where bookid={_bookid} and uid={_uid}
            lock in share mode
            '''.format(_uid=uid,_bookid=bookid)
        cursor.execute(sql)
        print(sql)
        if(len(cursor.fetchall())>0):
            response_object['status']='already_buyed'
            return jsonify(response_object)

        # 添加购买记录，更新库存以及书的已购买字段，使用事务处理，如果信誉分达到上限，则不再增加
        try:
            now=datetime.date.today()
            cursor.callproc('add_buy',(bookid,uid,now,price,round(discount,2)))
            print("callproc add_buy")
            mydb.commit()
            mydb.close()
            response_object['balance']=balance-final_price
            return jsonify(response_object)
        except:
            mydb.rollback()
            mydb.close()
            response_object['status']='buy_failed'
            return jsonify(response_object)

    # 查看用户的购买记录
    elif(message=='get_buy_list'):
        # 查看记录，使用guest
        mydb = mysql.connector.connect(
            host="localhost",
            user="guest",
            passwd="guest",
            database="bms"
        )
        cursor = mydb.cursor()
        BUY_LIST=[]  # 返回给前端的购买记录
        username=post_data.get('username')

        # 获取余额
        sql='''
            select balance from users where username like '{un}'
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        data=cursor.fetchall()
        balance=data[0][0]
        response_object['balance']=balance

        # 获取购买记录
        sql='''
            select buy.bookid, books.bookname, books.author, books.publisher, buy.buydate, buy.price, buy.discount
            from buy, books
            where buy.bookid=books.bookid and buy.uid in (
                select uid from users where username like '{un}'
            )
            lock in share mode
            '''.format(un=username)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            consume=0.00
            for i in range(len(sch_result)):
                BUY_LIST.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'author': sch_result[i][2],
                    'publisher': sch_result[i][3],
                    'buydate': str(sch_result[i][4]), 
                    'price': sch_result[i][5],
                    'discount': round(sch_result[i][6],2)*10,
                    'after_price': round(sch_result[i][5]*sch_result[i][6],2),
                })
                consume=consume+round(sch_result[i][5]*sch_result[i][6],2)
            mydb.commit()
            mydb.close()
            response_object['byl']=BUY_LIST
            response_object['consume']=round(consume,2)
            response_object['status']='get_buy_list_successfully'
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='get_buy_list_failed'
            return jsonify(response_object)    

#POST /admin 管理员操作
@app.route('/admin', methods=['POST'])
def manage():
    response_object = {'status': 'success'}
    # 连接数据库，使用root完成所有操作
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="bms"
    )
    cursor = mydb.cursor()
    post_data = request.get_json()
    message = post_data.get('message')

    # 更新库存
    if(message=='chg_bookinfo'):
        bookid=post_data.get('bookid')
        price=post_data.get('price')
        stock_num=post_data.get('stock_num')
        try:
            cursor.callproc('chg_bookinfo',(bookid,stock_num,price))
            print("callproc chg_bookinfo")
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)
    
    # 管理借阅
    elif(message=='get_allusr_borrowlist'):
        # 原理与单个用户的借阅列表相同，只不过不再用uid的限制
        ALLUSRBL=[]
        sql='''
            select borrow.bookid,borrow.uid,users.username,books.bookname,startdate,enddate,isexpired,iscalculated, datediff(enddate,CURDATE()) remain
            from borrow,users,books
            where borrow.uid=users.uid and borrow.bookid=books.bookid
            order by remain
            lock in share mode
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            now=datetime.date.today() # 当前时间

            # 对于每一条记录，在插入前需要进行过期检查
            for i in range(len(sch_result)):
                # 标记借阅是否开始
                if(now>=sch_result[i][4]):
                    isstarted=True
                    # 只统计未计算逾期的借阅记录
                    if(sch_result[i][5]<now and sch_result[i][7]==False):
                        cursor.callproc('cal_expired',(sch_result[i][0],sch_result[i][1])) # 记录该逾期
                        cursor.callproc('minus_credit',(10,sch_result[i][1])) # 更新用户的信誉分，存储过程实现
                else:
                    isstarted=False
                ALLUSRBL.append({
                    'bookid': sch_result[i][0],
                    'uid': sch_result[i][1],
                    'username': sch_result[i][2],
                    'bookname': sch_result[i][3],
                    'startdate': str(sch_result[i][4]), 
                    'enddate': str(sch_result[i][5]),
                    'isexpired': sch_result[i][6],
                    'iscalculated': sch_result[i][7],
                    'isstarted': isstarted,
                    'remain': sch_result[i][8],
                })
            mydb.commit()
            mydb.close()
            response_object['allusrbl']=ALLUSRBL
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)
    
    # 还书
    elif(message=='return_book'):
        uid=post_data.get('uid')
        bookid=post_data.get('bookid')
        # 判断借阅是否逾期，逾期是否已记录
        sql='''
            select isexpired,iscalculated
            from borrow
            where bookid={bi} and uid={ui}
            lock in share mode
            '''.format(bi=bookid,ui=uid)
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchall()
        isexp=data[0][0]
        iscal=data[0][1]
        if(isexp and (not iscal)):
            # 扣除信誉分，改为已经记录
            cursor.callproc('cal_expired',(bookid,uid))
            mydb.commit()
            cursor.callproc('minus_credit',(10,uid))
            mydb.commit()

        # 删除借阅记录，更新用户借阅数量，更新库存，事务完成
        try:
            cursor.callproc('delete_borrow',(bookid,uid))
            print("callproc delete_borrow")
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.rollback()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)

    # 获得销售列表
    elif(message=='get_buylist'):
        # 原理与单用户的购买列表相同，不再用uid限制
        BUYLIST=[]
        sql='''
            select buy.bookid,buy.uid,users.username,books.bookname,books.author,books.publisher,buydate,buy.price,buy.discount
            from buy,users,books
            where buy.uid=users.uid and buy.bookid=books.bookid
            order by buy.uid
            lock in share mode
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                BUYLIST.append({
                    'bookid': sch_result[i][0],
                    'uid': sch_result[i][1],
                    'username': sch_result[i][2],
                    'bookname': sch_result[i][3],
                    'author': sch_result[i][4],
                    'publisher': sch_result[i][5],
                    'buydate': str(sch_result[i][6]), 
                    'price': sch_result[i][7],
                    'discount': round(sch_result[i][8],2),
                    'sale': round(sch_result[i][7]*sch_result[i][8],2),
                })
            mydb.commit()
            mydb.close()
            response_object['buylist']=BUYLIST
            return jsonify(response_object)
        except:
            response_object['status']='failed'
            return jsonify(response_object)
    
    # 获得畅销榜
    elif(message=='get_topsale'):
        TOPSALE=[]
        sql='''
            select *
            from books
            order by purchased desc
            limit 0,20
            lock in share mode
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                TOPSALE.append({
                    'listindex': i+1,
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'author': sch_result[i][2],
                    'publisher': sch_result[i][3],
                    'publishdate': str(sch_result[i][4]),
                    'price': sch_result[i][5],
                    'storage': sch_result[i][6],
                    'readed': sch_result[i][7],
                    'purchased': sch_result[i][8]
                })
            mydb.commit()
            mydb.close()
            response_object['topsale']=TOPSALE
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)

    # 统计销售额
    elif(message=='get_profit'):
        sql='''
            select sum(price*discount)
            from buy
            lock in share mode
            '''
        cursor.execute(sql)
        print(sql)
        response_object['all_profit']=cursor.fetchone()[0]
        mydb.commit()
        mydb.close()
        return jsonify(response_object)
    
    # 获取用户列表
    elif(message=='get_allusr'):
        ALLUSR=[]
        sql='''
            select *
            from users
            order by uid
            lock in share mode
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                ALLUSR.append({
                    'uid': sch_result[i][0],
                    'username': sch_result[i][1],
                    'password': sch_result[i][2],
                    'credit': sch_result[i][3],
                    'balance': sch_result[i][4],
                    'borrownum': sch_result[i][5],
                    'level': sch_result[i][6],
                })
            mydb.commit()
            mydb.close()
            response_object['allusr']=ALLUSR
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)
    
    # 更新用户，请求当前用户的可修改信息
    elif(message=='update_usr'):
        uid=post_data.get('uid')
        sql='''
            select credit,balance,level
            from users
            where uid={ui}
            lock in share mode
            '''.format(ui=uid)
        cursor.execute(sql)
        print(sql)
        usrinfo=cursor.fetchone()
        CUR_USR={
            'credit': usrinfo[0],
            'balance': usrinfo[1],
            'level': usrinfo[2],
        }
        mydb.commit()
        mydb.close()
        response_object['cur_usr']=CUR_USR
        return jsonify(response_object)
    
    # 确认修改
    elif(message=='commit_update'):
        uid=post_data.get('uid')
        credit=post_data.get('credit')
        balance=post_data.get('balance')
        level=post_data.get('level')
        try:
            cursor.callproc('update_usrinfo',(uid,credit,balance,level))
            print('callproc update_usrinfo')
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)
    
    # 重置密码为000000
    elif(message=='reset_passwd'):
        uid=post_data.get('uid')
        username=post_data.get('username')
        raw_passwd='000000'
        hash = hashlib.md5()
        hash.update(bytes(username+raw_passwd, encoding='utf-8'))
        try:
            # 重置密码，调用修改密码过程
            cursor.callproc('chg_passwd',(username,str(hash.hexdigest()),uid))
            print("callproc chg_passwd")
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)
    
    # 进货新书
    elif(message=="stock_book"):
        bookname=post_data.get('bookname')
        author=post_data.get('author')
        publisher=post_data.get('publisher')
        publishdate=post_data.get('publishdate')
        price=post_data.get('price')
        storage=post_data.get('storage')

        try:
            cursor.callproc('stock_book',(bookname,author,publisher,publishdate,price,storage))
            print('callproc stock_book')
            mydb.commit()
            mydb.close()
            return jsonify(response_object)

        except:
            mydb.rollback()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)


# POST /top 获取榜单
@app.route('/top', methods=['POST'])
def top():
    response_object = {'status': 'success'}
    # 连接数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="guest",
        passwd="guest",
        database="bms"
    )
    cursor = mydb.cursor()
    post_data = request.get_json()
    message = post_data.get('message')

    # 热书榜
    if(message=='top_readed'):
        TOPREADED=[]
        sql='''
            select *
            from books
            order by readed desc
            limit 0,20
            lock in share mode
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                TOPREADED.append({
                    'listindex': i+1,
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'author': sch_result[i][2],
                    'publisher': sch_result[i][3],
                    'publishdate': str(sch_result[i][4]),
                    'price': sch_result[i][5],
                    'storage': sch_result[i][6],
                    'readed': sch_result[i][7],
                })
            mydb.commit()
            mydb.close()
            response_object['topreaded']=TOPREADED
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)

# POST /comment 添加书评
@app.route('/comment', methods=['POST'])
def comment():
    response_object = {'status': 'success'}
    post_data = request.get_json()
    message = post_data.get('message')

    if(message=='comment'):
        # 添加书评，使用root
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="bms"
        )
        cursor = mydb.cursor()
        bookid=post_data.get('bookid')
        username=post_data.get('username')
        comment=post_data.get('comment')
        now=datetime.date.today()
        sql='''
            select uid
            from users
            where username like '{un}'
            lock in share mode
            '''.format(un=username)
        cursor.execute(sql)
        uid=cursor.fetchone()[0]
        try:
            cursor.callproc('add_comment',(bookid,uid,comment,now))
            print("callproc add_comment")
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)
    
    elif(message=='view_comment'):
        # 查看书评，使用guest
        mydb = mysql.connector.connect(
            host="localhost",
            user="guest",
            passwd="guest",
            database="bms"
        )
        cursor = mydb.cursor()
        bookid=post_data.get('bookid')
        COMMENTS=[]
        sql='''
            select cid,users.username,content,cdate
            from comment,users
            where comment.uid=users.uid
            and comment.bookid={bi}
            order by cdate desc
            limit 0,10
            lock in share mode
            '''.format(bi=bookid)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                COMMENTS.append({
                    'cid': sch_result[i][0],
                    'username': sch_result[i][1],
                    'content': sch_result[i][2],
                    'cdate': str(sch_result[i][3]),
                })
            mydb.commit()
            mydb.close()
            response_object['comment_list']=COMMENTS
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)

    elif(message=='delete_comment'):
        # 删除书评，使用root
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="bms"
        )
        cursor = mydb.cursor()
        cid=post_data.get('cid')

        try:
            sql='''
                delete from comment
                where cid={ci}
                '''.format(ci=cid)
            cursor.execute(sql)
            print(sql)
            mydb.commit()
            mydb.close()
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)

    elif(message=='get_all_comment'):
        # 获取全部书评，使用guest
        mydb = mysql.connector.connect(
            host="localhost",
            user="guest",
            passwd="guest",
            database="bms"
        )
        cursor = mydb.cursor()

        ALLCOMMENT=[]
        sql='''
            select cid, books.bookid, books.bookname, users.uid, users.username, content, cdate
            from comment,users,books
            where comment.uid=users.uid and comment.bookid=books.bookid
            order by cdate desc, bookid
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                ALLCOMMENT.append({
                    'cid': sch_result[i][0],
                    'bookid': sch_result[i][1],
                    'bookname': sch_result[i][2],
                    'uid': sch_result[i][3],
                    'username': sch_result[i][4],
                    'content': sch_result[i][5],
                    'cdate': str(sch_result[i][6]),
                })
            mydb.commit()
            mydb.close()
            response_object['all_comment_list']=ALLCOMMENT
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='failed'
            return jsonify(response_object)

if __name__ == '__main__':
    app.run()