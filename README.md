# DBFinalProject
Final Project of Database Course -- A book management system

Developed by html, CSS(Element-UI), JavaScript (Using Vue framework) and python.



## 2020/12/6 Updates

### The Front End

--Complete users' login interface and search interface without CSS.

--Users can search books by book name, author and publisher now.

### The Back End

--Complete the interaction of login and register.

--Complete the book searching process.



## 2020/12/11 Updates

### The Front End

--Complete modification function for users, including modifying their usernames and passwords.

--Allow users to check their list of borrowed books and cancel their choices.

--Combine Vue2.x with Element-UI for CSS implementation.

### The Back End

--Complete the update process of user's information.

--Complete the update process of book resources and users' borrow lists, which will change correspondingly after user's operation.

## 2020/12/17 Updates

### The Front End

--Allow users to check their buy list.

--Allow users to make comments on certain books and view top 20 comment on that book.

#### Add user interface for admin

--Admin can view all basic information of books in the database and stock old or new books.

--Admin can manage users' borrow list, deciding whether lengthen their borrowing period or not and deleting the borrow record when user return their books.

--Admin can view all the orders of buying book and the sum of sale.

--Admin can manage all users in the system by editing their credit, balance and level.

### The Back End

--Complete all the functions corresponding to the newly appended operation of users.

--Use MySQL procedure to replace "insert", "update" and "delete" orders.

--Add prevention of MySQL injection.

--Divide all functions into two groups for safety reasons, one using account "guest" for accessing the database and the other one using account "root" for accessing the database.

## Reference Material

[Flask和Vue.js构建全栈单页面web应用【通过Flask开发RESTful API】](https://zhuanlan.zhihu.com/p/76588212)

[Element-UI中文文档](https://element.eleme.cn/#/zh-CN/component/input)

[Vue.js菜鸟教程](https://www.runoob.com/vue2/vue-tutorial.html)

[MySQL 存储过程](https://www.runoob.com/w3cnote/mysql-stored-procedure.html)

[Python MySQL教程](https://www.qikegu.com/docs/3263)

[mysql.connector 事务总结](https://www.cnblogs.com/yaoyu126/p/6413638.html)
