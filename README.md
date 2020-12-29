# DBFinalProject

## 数据库期末项目

数据库系统基础课程期末项目——图书管理系统

采用HTML(Element-UI), CSS, JavaScript(采用Vue框架)和Python开发

Final Project of Database Course -- A book management system

Developed by html(Element-UI), CSS, JavaScript (Using Vue framework) and python.

## 项目结构 The Project Structure

dbfinalproject

│  procedure_defination  --MySQL存储过程定义

│  server.py  --服务器主程序

│

└──db_manip  --数据库初始化脚本

│  	│  bookinfo.xlsx  --图书信息

│  	│  create_db.py  --创建数据库脚本

│  	│  get_book_info.py  --当当网爬虫获取图书信息脚本

│  	│  insert_book_info.py  --将图书信息插入数据库脚本

│  	│  insert_user_info.py  --创建管理员用户脚本

│  

└──static  --静态资源

│  	│  admin_bg.jpg  --管理员界面背景

│  	│  login_bg.png  --登录/注册界面背景

│  	│  main_bg.png  --主界面背景

│  	│  vue.js  --vue@2.6.12对应js文件

│  	│  index.css  --element-ui@2.14.1对应css文件

│  	│  index.js  -- element-ui@2.14.1对应js文件

│  	│  axios.min.js  --axios@0.21.0对应js文件

│  

└──templates  --html文件夹

  	  │  login.html  --登录界面

  	  │  regist.html  --注册界面

  	  │  book.html  --用户主界面

  	  │  admin.html  --管理员界面

## 系统使用说明 System Instructions

1. 安装MySQL及Python相关库，使用root账户创建数据库bms（在本系统中root密码为root）；

   Install MySQL and Python related libraries, and create database BMS with root account (root password in this system is 'root'); 

2. 使用***create_db.py***在bms数据库中建立关系模式；

   Run ***create_db.py*** to establish tables in BMS database;

3. 在MySQL中创建用户guest，密码设置为guest，对用户guest赋予bms中所有表的SELECT权限；

   Create a user named "guest" in MySQL, set the password as "guest", and give the user "guest" the SELECT privilege of all tables in BMS;

4. 接着用Python爬虫***get_bookinfo.py***从当当网获取图书数据，获得csv数据文件，用Excel转化为xlsx文件后，运行***insert_book_info.py***将图书信息导入到bms数据库中；

   Then run ***get_bookinfo.py***, a Python crawler, was used to obtain book data and CSV data file from Dangdang.com. After CSV file was converted into XLSX file, ***insert_book_info.py*** was run to import book information into BMS database.

5. 最后运行***insert_user_info.py***，插入管理员用户admin和指定的某一普通用户（需输入用户名和密码），即可完成系统的前期准备工作。之后运行***server.py***即可开始运行系统。

   Finally, run ***insert_user_info.py***, insert administrator user "admin" and some ordinary user specified (user name and password need to be entered), and the preparatory work of the system can be completed. Then run ***server.py*** to start running the system.

## 更新日志 Update Log 

## 2020/12/29 Updates

### The Front End 前端

--注册界面添加了密码确认框

--Added input box for password confirmation when registering.

### The Back End 后端

--添加了处理注册时两次密码不一致的逻辑

--Added logic to handle two inconsistent passwords when registering.

## 2020/12/27 Updates

### The Front End 前端

--修改了图书查找界面的列宽，使五位数书号不再换行

--修复了管理员按书评内容搜索时无法正确过滤的问题

--为错误消息提示增加了图标

--修复了管理员查看用户借阅记录按书名进行搜索后借阅状态显示不对的问题

--对于未开始的借阅，为管理员添加了强制取消该借阅的功能

--Modified the column width of the book search interface, so that the five-digit bookid no longer breaks a line

--Fixed an issue where admin could not properly filter by book review content.

--Added icons for error messages.

--Fixed the problem that the admin checked the user's borrowing record and searched by title, and the borrowing status was not displayed correctly.

--For the borrow record which is not start, admin can cancel them now.

### The Back End 后端

--优化了注册界面注册失败后的提示信息

--增加了对应强制取消借阅的处理逻辑

--Optimized the prompt message after registration failure.

--Added processing logic for mandatory cancellations.

## 2020/12/26 Updates

### The Front End 前端

--为管理员修改用户信息对话框增加了取消按钮，用户等级由输入框改为了选择

--Add CANCEL button to the dialog for admin to adjust users' information, change the input box of user level to selection box.

## 2020/12/25 Updates

### The Front End 前端

--修复了管理员界面无法正常显示借阅逾期的问题

--Fixed an issue where the admin interface could not properly display borrowing record which is expired.

## 2020/12/23 Updates

### The Front End 前端

--为按钮添加了图标

--优化了用户界面，调整了表格、按钮的间距，调整了字符的字体和颜色

--优化了日期选择器，允许用户在当日起的45天内选择借阅起止日期

--用户现在可以在借阅列表中看到借阅的剩余时间

--引入了折扣这以新的属性，书籍的实际成交价现在与书籍的售价和折扣相关，折扣与用户的信誉分相关

--允许管理员可以进货新的书籍

--允许管理员可以通过两种方式管理书籍评论，第一是在某一书籍下删除对应书籍的评论，第二是在所有评论中搜索关键字来删除评论

--允许管理员可以重置用户的密码

--加入了本地引入vue, element-ui和vue.axios的方式

--Added icon and style for all buttons.

--Optimized the user interface, adjusted the spacing of tables and buttons, adjusted the font and color of characters

--Optimized the date selector, allowing users to select the borrowing start and end dates within 45 days from now.

--Users can now see the rest of the borrowing time in their borrowing lists.

--Add discount property which influence the buying process, now real price of a book depends on its initial price and the discount corresponding to users' credit.

--Admin can stock new books now.

--Admin can delete users' comments now in two ways, one is deleting comments by searching certain book, the other one is deleting comments by searching key words in comments.

--Admin can reset users' password when they forget.

--Added local method for installing Vue, Element-UI and vue.axios.

### The Back End 后端

--完成了前端对应功能的处理逻辑

--修改了一些SELECT语句，加入了到期时间

--调整了一些存储过程的定义，新增了进货新书的存储过程

--Completed the processing logic of the corresponding functions of the front end.

--Modified the SELECT query for getting borrow list, appending a new column about the remaining time user can keep that book.

--Changed some procedures' definitions.

## 2020/12/21 Updates

### The Front End 前端

--在用户界面添加了背景图片，调整了窗口的位置

--删除了续借功能

--允许用户查看他们的基本信息，包括除密码密文外的信息

--修复了一些bug

--Added a background image to the user interface and repositioned the window.

--The function of lengthening borrow time is deleted.

--Allows users to view their basic information, including information other than password ciphertext.

--Fixed some logical bugs.

### The Back End 后端

--完成了前端对应功能的处理逻辑

--用MySQL事务替换了一些关键操作，例如添加/删除用户的借阅/购买记录

--Added corresponding route for checking users' information.

--Used MySQL transactions to replace some key operations, such as add/delete borrow/buy record.

## 2020/12/17 Updates

### The Front End 前端

--允许用户查看他们的购买列表

--允许用户对书籍进行评论，并查看该书籍的最近10条评论

--Allows users to check their buy list.

--Allows users to make comments on certain books and view top 10 comment on that book.

#### Add user interface for admin 添加了管理员界面

--管理员可以查看数据库中所有图书的基本信息，也可以进货书籍（仅限旧书，即数据库中已有的书籍）

--管理员可以管理所有用户的借阅信息，并决定是否允许用户在借阅到期时续借，或者是处理用户的还书操作

--管理员可以查看所有用户的购买记录，统计总销售额

--管理员可以在后台修改用户的信誉分、余额和用户等级

--Admin can view all basic information of books in the database and stock old books.

--Admin can manage users' borrow list, deciding whether lengthen their borrowing period or not and deleting the borrow record when user return their books.

--Admin can view all the orders of buying book and the sum of sale.

--Admin can manage all users in the system by editing their credit, balance and level.

### The Back End 后端

--完成了前端对应功能的处理逻辑

--用MySQL存储过程替换了insert, update和delete操作

--加入了函数防止SQL注入攻击

--将数据库的访问分为guest和root两种身份，增加安全性

--Completed all the functions corresponding to the newly appended operation of users.

--Used MySQL procedure to replace "insert", "update" and "delete" orders.

--Added prevention of MySQL injection.

--Divided all functions into two groups for safety reasons, one using account "guest" for accessing the database and the other one using account "root" for accessing the database.

## 2020/12/11 Updates

### The Front End 前端

--完成了用户修改个人信息的功能，用户现在可以修改他们的用户名和密码

--允许用户借阅书籍，查看他们的借阅信息以及取消未开始的借阅

--在HTML文档中添加了vue@2.6.12框架和element-ui@2.14.1组件（@版本号）

--Completed modification function for users, including modifying their usernames and passwords.

--Allowed users to borrow books, check their list of borrowed books and cancel their choices.

--Combined vue@2.6.12 with Element-UI@2.14.1 (@version) in HTML documents.

### The Back End 后端

--完成了用户信息的更新功能

--完成了图书资源和用户借阅列表的更新功能，并可以在用户操作后正确改变它们的值

--Completed the update process of user's information.

--Completed the update process of book resources and users' borrow lists, which will change correspondingly after user's operation.

## 2020/12/6 Updates

### The Front End 前端

--完成了基本用户界面以及查询功能（不包括CSS部分）

--用户可以根据书名、作者和出版社信息对书籍进行查询

--Completed users' login interface and search interface without CSS.

--Users can search books by book name, author and publisher now.

### The Back End 后端

--完成了用户登录、注册过程的前后端交互

--完成了书籍搜索功能

--Completed the interaction of login and register.

--Completed the book searching process.

## 参考资料 Reference Material

[Flask和Vue.js构建全栈单页面web应用【通过Flask开发RESTful API】](https://zhuanlan.zhihu.com/p/76588212)

[Element-UI中文文档](https://element.eleme.cn/#/zh-CN/component/input)

[Vue.js菜鸟教程](https://www.runoob.com/vue2/vue-tutorial.html)

[MySQL 存储过程](https://www.runoob.com/w3cnote/mysql-stored-procedure.html)

[Python MySQL教程](https://www.qikegu.com/docs/3263)

[mysql.connector 事务总结](https://www.cnblogs.com/yaoyu126/p/6413638.html)

[第三篇 Python关于mysql的API--pymysql模块， mysql事务](https://www.cnblogs.com/victorm/p/9695876.html)

[el-table分页展示数据](https://blog.csdn.net/weixin_43412413/article/details/99696047)

[mysql.connector 事务总结](https://www.cnblogs.com/yaoyu126/p/6413638.html)