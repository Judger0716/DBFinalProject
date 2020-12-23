# DBFinalProject

## 数据库期末项目

数据库系统基础课程期末项目——图书管理系统

采用HTML(Element-UI), CSS, JavaScript(采用Vue框架)和Python开发

Final Project of Database Course -- A book management system

Developed by html(Element-UI), CSS, JavaScript (Using Vue framework) and python.

## 2020/12/6 Updates

### The Front End 前端

--完成了基本用户界面以及查询功能（不包括CSS部分）

--用户可以根据书名、作者和出版社信息对书籍进行查询

--Complete users' login interface and search interface without CSS.

--Users can search books by book name, author and publisher now.

### The Back End 后端

--完成了用户登录、注册过程的前后端交互

--完成了书籍搜索功能

--Complete the interaction of login and register.

--Complete the book searching process.

## 2020/12/11 Updates

### The Front End 前端

--完成了用户修改个人信息的功能，用户现在可以修改他们的用户名和密码

--允许用户借阅书籍，查看他们的借阅信息以及取消未开始的借阅

--在HTML文档中添加了vue@2.6.12框架和element-ui@2.14.1组件（@版本号）

--Complete modification function for users, including modifying their usernames and passwords.

--Allow users to borrow books, check their list of borrowed books and cancel their choices.

--Combine vue@2.6.12 with Element-UI@2.14.1 (@version) in HTML documents.

### The Back End 后端

--完成了用户信息的更新功能

--完成了图书资源和用户借阅列表的更新功能，并可以在用户操作后正确改变它们的值

--Complete the update process of user's information.

--Complete the update process of book resources and users' borrow lists, which will change correspondingly after user's operation.

## 2020/12/17 Updates

### The Front End 前端

--允许用户查看他们的购买列表

--允许用户对书籍进行评论，并查看该书籍的最近10条评论

--Allow users to check their buy list.

--Allow users to make comments on certain books and view top 10 comment on that book.

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

--Complete all the functions corresponding to the newly appended operation of users.

--Use MySQL procedure to replace "insert", "update" and "delete" orders.

--Add prevention of MySQL injection.

--Divide all functions into two groups for safety reasons, one using account "guest" for accessing the database and the other one using account "root" for accessing the database.

## 2020/12/21 Updates

### The Front End 前端

--在用户界面添加了背景图片，调整了窗口的位置

--删除了续借功能

--允许用户查看他们的基本信息，包括除密码密文外的信息

--修复了一些bug

--Add background image for all interfaces. Adjust the location and size of all the windows.

--Delete the function for admin to lengthen users' borrowing time.

--Users can check their basic information now.

--Logical bugs fixed.

### The Back End 后端

--完成了前端对应功能的处理逻辑

--用MySQL事务替换了一些关键操作，例如添加/删除用户的借阅/购买记录

--Add corresponding route for checking users' information.

--Use MySQL transactions to replace some key operations, such as add/delete borrow/buy record.

## 2020/12/23 Updates

### The Front End 前端

--为按钮添加了图标

--优化了用户界面，调整了表格、按钮的间距，调整了字符的字体和颜色

--优化了日期选择器，允许用户在当日起的两个月范围内选择借阅起止日期

--用户现在可以在借阅列表中看到借阅的剩余时间

--引入了折扣这以新的属性，书籍的实际成交价现在与书籍的售价和折扣相关，折扣与用户的信誉分相关

--允许管理员可以进货新的书籍

--允许管理员可以通过两种方式管理书籍评论，第一是在某一书籍下删除对应书籍的评论，第二是在所有评论中搜索关键字来删除评论

--允许管理员可以重置用户的密码

--加入了本地引入vue, element-ui和vue.axios的方式

--Add icon and style for all buttons.

--Adjust the user interface, including adjusting the space between different columns in tables, the space between buttons and some font sizes and colors.

--Adjust date-picker to allow users to choose dates in the period of two months.

--Users can now know how much longer they can keep the book.

--Add discount property which influence the buying process, now real price of a book depends on its initial price and the discount corresponding to users' credit.

--Admin can stock new books now.

--Admin can delete users' comments now in two ways, one is deleting comments by searching certain book, the other one is deleting comments by searching key words in comments.

--Admin can reset users' password when they forget.

--Add local method for installing Vue, Element-UI and vue.axios.

### The Back End 后端

--完成了前端对应功能的处理逻辑

--修改了一些SELECT语句，加入了到期时间

--调整了一些存储过程的定义，新增了进货新书的存储过程

--Add corresponding route and methods for new functions mentioned above.

--Alter the SELECT query for getting borrow list, appending a new column about the remaining time user can keep that book.

--Alter some procedures' definitions.

## Reference Material 参考资料

[Flask和Vue.js构建全栈单页面web应用【通过Flask开发RESTful API】](https://zhuanlan.zhihu.com/p/76588212)

[Element-UI中文文档](https://element.eleme.cn/#/zh-CN/component/input)

[Vue.js菜鸟教程](https://www.runoob.com/vue2/vue-tutorial.html)

[MySQL 存储过程](https://www.runoob.com/w3cnote/mysql-stored-procedure.html)

[Python MySQL教程](https://www.qikegu.com/docs/3263)

[mysql.connector 事务总结](https://www.cnblogs.com/yaoyu126/p/6413638.html)

[第三篇 Python关于mysql的API--pymysql模块， mysql事务](https://www.cnblogs.com/victorm/p/9695876.html)

[el-table分页展示数据](https://blog.csdn.net/weixin_43412413/article/details/99696047)

[mysql.connector 事务总结](https://www.cnblogs.com/yaoyu126/p/6413638.html)