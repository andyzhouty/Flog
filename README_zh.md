# LSFD202201V3

为LSFD202201项目所开发的博客程序

## 项目参与者

[Andy Zhou](https://github.com/z-t-y)

## 致谢

### 开源项目

- [Flask](https://github.com/pallets/flask)
- [Bootstrap](https://github.com/twbs/bootstrap)
- [Bootstrap-Flask](https://github.com/greyli/bootstrap-flask)
- [Flask-WTF](https://github.com/lepture/flask-wtf)
- [Flask-Share](https://github.com/greyli/flask-share)
- [MyQR](https://pypi.org/project/MyQR/)

### 书籍

- [Flask Web 开发实战](https://helloflask.com)

### 人员

- [GreyLi](https://greyli.com)

没有这些非常好的开源项目以及书籍，这个项目是不可能开发得了的。
同时，感谢 GreyLi，是他的《Flask Web 开发实战》带我走进了 Flask 世界

## 发行说明

### V3.8.4 2020-8-12

删除首页所有版本

### V3.8.2 & V3.8.3  2020-08-06 - 2020-08-11

修复一些 BUG

### V3.8.1 2020-08-05

去除了多线程发送邮件（不知什么原因，多线程无法工作）

### V3.8.0 2020-08-04

1. 编写更多单元测试
2. 添加留言板
3. 添加测试覆盖率

### V3.7.1 版本 2020-07-30

1. 修复管理员不能删除文章的 Bug
2. 更新 README.md 文档

### V3.7.0 版本 2020-07-29

1. 使用蓝本重构代码
2. 在上传文章时向管理员发送邮件
3. 使用 Flask-Migrate 迁移数据库
4. 使用 MySQL 替换掉 SQLite
5. 使用 unittest 编写基本单元测试

### V3.6.1 版本 2020-07-24

1. 重构代码
2. 使用 CKEditor

### V3.5.0 版本 2020-07-23

1. 把首页的黑底换成浅灰色底
2. 增强分页效果
3. 重构项目

### V3.4.0 版本 2020-07-20

1. 给予管理员更改文章的权限
2. 用[Bootstrap-Flask](https://github.com/greyli/bootstrap-flask)以及[Bootstrap4](https://github.com/twbs/bootstrap)重构代码
3. 在首页上添加淡进效果
4. 在上传文章页面添加日期选择器
