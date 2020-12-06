from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
import mysql.connector
import hashlib

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
        select password
        from users
        where username='%s'
        ''' % (request.form['username']))
    print(sql)
    cursor.execute(sql)
    values=cursor.fetchall()
    print(values)
    # 如果无此用户，则返回错误
    if(len(values)==0):
        mydb.commit()
        mydb.close()
        return render_template('login.html',msg='无此用户')
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
        user="guest",
        passwd="guest",
        database="bms"
    )
    cursor = mydb.cursor()
    post_data=request.get_json()
    bookname=post_data.get('bookname')
    author=post_data.get('author')
    publisher=post_data.get('publisher')
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

if __name__ == '__main__':
    app.run()