from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
import mysql.connector
import hashlib
import datetime

app = Flask(__name__)

# 防止SQL注入过滤器
def isValid(sql):
    init_len=len(sql)
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
    return render_template('login.html',msg='请输入用户名和密码登录')


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

    # 获得当前用户名对应的密码
    if(isValid(request.form['username'])):
        sql=('''
        select password,level
        from users
        where username='%s'
        ''' % (request.form['username']))
        cursor.execute(sql)
        print(sql)
    else:
        return render_template('login.html',msg='用户名或密码不正确')
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
    if(isValid(request.form['username']) and isValid(request.form['password'])):
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

# POST /chginfo 修改已注册的用户信息
@app.route('/chginfo', methods=['POST'])
def change_info():
    response_object = {'status': 'success'}
    post_data=request.get_json()
    before_username=post_data.get('before_username')
    before_password=post_data.get('before_password')
    after_username=post_data.get('after_username')
    after_password=post_data.get('after_password')

    # 修改后的用户名和密码含有非法字符
    if(not isValid(after_username) or not isValid(after_password)):
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
                'publishdate': sch_result[i][4],
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

        # 如果借阅起始日期早于今日，不合法
        now=datetime.date.today() # 当前时间
        
        # 为了测试数据库，这一要求可以暂时去掉
        '''
        sd=datetime.date(int(startdate[:4]),int(startdate[5:7]),int(startdate[8:10]))
        if(sd<now):
            response_object['status']='invalid_date'
            return jsonify(response_object)
        '''

        # 更新用户的信誉分，存储过程实现
        sql='''
            select borrow.bookid,borrow.uid,enddate,iscalculated
            from borrow,users
            where borrow.uid=users.uid and users.username='{un}'
            and iscalculated=false
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

        # 添加借阅记录，更新库存以及书的已阅读字段，事务实现
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
            now=datetime.date.today() # 当前时间
            for i in range(len(sch_result)):
                if(now>=sch_result[i][2]):
                    isstarted=True
                else:
                    isstarted=False
                BORROW_LIST.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'startdate': sch_result[i][2], 
                    'enddate': sch_result[i][3],
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
            '''.format(bi=bookid,un=username)
        cursor.execute(sql)
        if(len(cursor.fetchall())>0):
            # 删除未开始的借阅记录（是否开始由isstarted和isexpired共同决定），事务实现
            sql='''
                delete from borrow
                where bookid={bi} 
                and uid in (select uid from users where username like '{un}')
                '''.format(bi=bookid,un=username)
            cursor.execute(sql)
            print(sql)
            # 减少信誉分，已借阅数减少
            sql='''
                update users
                set credit=credit-10, borrownum=borrownum-1
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
            # 如果库存为0，则不允许购买
            if(storage==0):
                response_object['status']='no_storage'
                return jsonify(response_object)
            else:
                # 否则告知客户端可以购买
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

        # 获取uid
        sql='''
            select uid,balance from users where username like '{un}'
            '''.format(un=username)
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchall()
        uid=data[0][0]
        balance=data[0][1]

        # 获取书价
        sql='''
            select price from books
            where bookid={bi}
            '''.format(bi=bookid)
        cursor.execute(sql)
        print(sql)
        price=cursor.fetchone()[0]

        # 余额不足，拒绝
        if(balance<price):
            response_object['status']='low_balance'
            return jsonify(response_object)
        
        # 重复购买，拒绝
        sql='''
            select bookid from buy
            where bookid={_bookid} and uid={_uid}
            '''.format(_uid=uid,_bookid=bookid)
        cursor.execute(sql)
        print(sql)
        if(len(cursor.fetchall())>0):
            response_object['status']='already_buyed'
            return jsonify(response_object)

        # 添加购买记录，更新库存以及书的已购买字段，使用事务处理
        now=datetime.date.today()
        sql='''
            insert into buy
            values ({_bookid},{_uid},'{bd}',{p})
            '''.format(_bookid=bookid,_uid=uid,bd=now,p=price)
        try:
            cursor.execute(sql)
            print(sql)
            # 更新书籍的库存，销量
            sql='''
                update books
                set storage=storage-1, purchased=purchased+1
                where bookid={_bookid}
                '''.format(_bookid=bookid)
            cursor.execute(sql)
            print(sql)
            # 更新用户的余额与信誉分
            sql='''
                update users
                set balance=balance-{p},credit=credit+10
                where uid={_uid}
                '''.format(p=price,_uid=uid)
            cursor.execute(sql)
            print(sql)
            mydb.commit()
            mydb.close()
            response_object['balance']=balance-price
            return jsonify(response_object)

        except:
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
        BUY_LIST=[]
        username=post_data.get('username')

        # 获取余额
        sql='''
            select balance from users where username like '{un}'
            '''.format(un=username)
        cursor.execute(sql)
        data=cursor.fetchall()
        balance=data[0][0]
        response_object['balance']=balance

        sql='''
            select buy.bookid, books.bookname, buy.buydate, buy.price
            from buy, books
            where buy.bookid=books.bookid and buy.uid in (
                select uid from users where username like '{un}'
            )
            '''.format(un=username)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                BUY_LIST.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'buydate': sch_result[i][2], 
                    'price': sch_result[i][3],
                })
            mydb.commit()
            mydb.close()
            response_object['byl']=BUY_LIST
            response_object['status']='get_buy_list_successfully'
            return jsonify(response_object)
        except:
            mydb.commit()
            mydb.close()
            response_object['status']='get_buy_list_failed'
            return jsonify(response_object)    

#POST /admin 管理员操作
@app.route('/admin', methods=['POST'])
def manage_book():
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
    if(message=='stock_book'):
        bookid=post_data.get('bookid')
        stock_num=post_data.get('stock_num')
        try:
            cursor.callproc('stock_book',(stock_num,bookid))
            print("callproc stock_book")
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
        ALLUSRBL=[]
        sql='''
            select borrow.bookid,borrow.uid,users.username,books.bookname,startdate,enddate,isexpired,iscalculated
            from borrow,users,books
            where borrow.uid=users.uid and borrow.bookid=books.bookid
            order by borrow.uid
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                ALLUSRBL.append({
                    'bookid': sch_result[i][0],
                    'uid': sch_result[i][1],
                    'username': sch_result[i][2],
                    'bookname': sch_result[i][3],
                    'startdate': sch_result[i][4], 
                    'enddate': sch_result[i][5],
                    'isexpired': sch_result[i][6],
                    'iscalculated': sch_result[i][7],
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
    
    # 续借一周
    elif(message=='renew_borrow'):
        bookid=post_data.get('bookid')
        uid=post_data.get('uid')
        now=datetime.date.today()
        # 逾期/未开始，不能续借
        sql='''
            select startdate,isexpired
            from borrow
            where bookid={bi} and uid={ui}
            '''.format(bi=bookid,ui=uid)
        cursor.execute(sql)
        print(sql)
        data=cursor.fetchall()
        sd=data[0][0]
        isexp=data[0][1]
        if(now<sd or isexp):
            response_object['status']='failed'
            return jsonify(response_object)
        
        sql='''
            update borrow
            set enddate=enddate+7
            where uid={ui} and bookid={bi}
            '''.format(ui=uid,bi=bookid)
        try:
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
    
    # 还书
    elif(message=='return_book'):
        uid=post_data.get('uid')
        bookid=post_data.get('bookid')
        # 判断借阅是否逾期，逾期是否已记录
        sql='''
            select isexpired,iscalculated
            from borrow
            where bookid={bi} and uid={ui}
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

        # 删除借阅记录，事务完成
        sql='''
            delete from borrow
            where bookid={bi} and uid={ui}
            '''.format(bi=bookid,ui=uid)
        cursor.execute(sql)
        print(sql)    
        # 更新用户借阅数量
        sql='''
            update users
            set borrownum=borrownum-1
            where uid={ui}
            '''.format(ui=uid)
        cursor.execute(sql)
        print(sql)
        # 更新库存
        sql='''
            update books
            set storage=storage+1
            where bookid={bi}
            '''.format(bi=bookid)
        cursor.execute(sql)
        print(sql)

        mydb.commit()
        mydb.close()
        return jsonify(response_object)

    # 获得销售列表
    elif(message=='get_buylist'):
        BUYLIST=[]
        sql='''
            select buy.bookid,buy.uid,users.username,books.bookname,buydate,buy.price
            from buy,users,books
            where buy.uid=users.uid and buy.bookid=books.bookid
            order by buy.uid
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
                    'buydate': sch_result[i][4], 
                    'price': sch_result[i][5],
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
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                TOPSALE.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'author': sch_result[i][2],
                    'publisher': sch_result[i][3],
                    'publishdate': sch_result[i][4],
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
            select sum(price)
            from buy
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
        sql='''
            update users
            set credit={cd},balance={bl},level={lv}
            where uid={ui}
            '''.format(cd=credit,bl=balance,lv=level,ui=uid)
        try:
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

# POST /top 获取热书榜
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

    if(message=='top_readed'):
        TOPREADED=[]
        sql='''
            select *
            from books
            order by readed desc
            limit 0,20
            '''
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                TOPREADED.append({
                    'bookid': sch_result[i][0],
                    'bookname': sch_result[i][1],
                    'author': sch_result[i][2],
                    'publisher': sch_result[i][3],
                    'publishdate': sch_result[i][4],
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
            select users.username,content,cdate
            from comment,users
            where comment.uid=users.uid
            and comment.bookid={bi}
            order by cdate desc
            limit 0,10
            '''.format(bi=bookid)
        try:
            cursor.execute(sql)
            print(sql)
            sch_result=cursor.fetchall()
            for i in range(len(sch_result)):
                COMMENTS.append({
                    'username': sch_result[i][0],
                    'content': sch_result[i][1],
                    'cdate': sch_result[i][2],
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


if __name__ == '__main__':
    app.run()