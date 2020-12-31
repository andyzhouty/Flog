# <img src="https://flog.pythonanywhere.com/static/favicon/favicon.svg" width="50px"> Flog
[英文版](./README.md)  
[![Documentation Status](https://img.shields.io/readthedocs/flog?logo=Read%20The%20Docs&style=for-the-badge)](https://flog.readthedocs.io/en/latest/?badge=latest)
[![CircleCI Status](https://img.shields.io/circleci/build/github/z-t-y/Flog?logo=circleci&style=for-the-badge)](https://circleci.com/gh/z-t-y/Flog)
[![TravisCI Status](https://img.shields.io/travis/z-t-y/Flog?logo=travis&style=for-the-badge)](https://travis-ci.com/github/z-t-y/Flog)
[![Coverage Status](https://img.shields.io/coveralls/github/z-t-y/Flog?logo=coveralls&style=for-the-badge)](https://coveralls.io/github/z-t-y/Flog?branch=master)

由[Freepik]("https://www.flaticon.com/authors/freepik")制作的图标
在Flask学习期间创建的博客网站。

## 维护者

[z-t-y(Github)](https://github.com/z-t-y)
[andyzhouty(Gitee)](https://gitee.com/andyzhouty)

## 致谢

### 项目

- [Flask](https://github.com/pallets/flask)
- [Bootstrap](https://github.com/twbs/bootstrap)
- [Bootstrap-Flask](https://github.com/greyli/bootstrap-flask)
- [Flask-WTF](https://github.com/lepture/flask-wtf)

### 书籍

- [《Flask Web开发实战》](https://helloflask.com)，[李辉](https://greli.com)著
- [《Flask Web开发》](https://www.ituring.com.cn/book/2463), [Miguel Grinberg](https://blog.miguelgrinberg.com/)著，安道译

### 人员

- [李辉](https://greyli.com)

没有这些功能完备且维护良好的项目，这个网站无法成为现在的样子。同时，感谢李辉，是他的《Flask Web开发》带我走进了Flask的美好世界。

## 功能

- 登录、注册(需要邮箱验证)、登出、注销账户
- 收藏文章
- 关注用户
- 撰写文章
- 评论文章
- 消息中心
- 双语言支持 (简体中文和美式英语)
- Web API

## API 文档

[ReadTheDocs](https://flog.readthedocs.io/en/latest/?)

## 在本地运行这个网站

### 部署网站到本地

如果你使用pip+requirements.txt，命令如下：

```shell
git clone https://github.com/z-t-y/Flog.git ./flog # 或git clone https://gitee.com/andyzhouty/Flog.git ./flog
cd flog/
python3 -m venv venv # 如果你使用Windows,请替换为 python -m venv venv
source ./venv/bin/activate # 如果你使用Windows，请替换为 ./venv/Scripts/activate
pip3 install -r requirements/dev.txt # 安装相关依赖
flask deploy # 初始化数据库
flask forge # 生成虚拟数据
flask create-admin
flask run
```

如果你使用pipenv，命令如下：

```shell
# 克隆项目并切换到相应目录（如上）
pipenv install # 使用pipenv安装相关依赖
pipenv shell
flask deploy # 初始化数据库
flask forge
flask create-admin
flask run
```

应用配置默认值：

| 配置名            |  FLOG_EMAIL | FLOG_EMAIL_PASSWORD | FLOG_ADMIN | FLOG_ADMIN_EMAIL | FLOG_ADMIN_PASSWORD |
| ---           | ----------- | ------------------- | ---------- | ---------------- | ------------------- |
| 默认值 | flog_admin@example.com | flog_email_password | flog_admin | flog_admin@example.com | flog_admin_password |
| 描述 | flog部署服务器的邮箱（可以使用个人邮箱） | `FLOG_EMAIL`的密码 | 管理员用户的用户名 | 管理员邮箱账号 | 管理员密码

### 运行单元测试

pip+requirements.txt

```shell
# 假设已经激活了虚拟环境
pip3 install -r requirements/dev.txt
flask test
```

pipenv

```shell
pipenv install --dev
pipenv shell
pytest
```

注意:
如果`test_push_notification`测试运行报错且报错信息如下

```text
sqlite3.InterfaceError Error binding parameter 0...
```

这应该是由sqlite3对某些数据类型的不支持引起的,你应该指定`DATABASE_TEST`环境变量来
把默认的sqlite内存型数据库替换为PostgreSQL或MySQL等数据库。

## 关于一些小问题

1. 为什么这个项目名为'Flog'?  
   'Flog'是Flask和Blog这两个词的组合，这个词听起来（以及看起来）像'frog'，所以我用了一只青蛙作为网站的图标。

2. 为什么这个网站有时一天有好几条提交，却有时候连续几周没有提交？  
这个网站不能及时更新因为我是一名学生（作业有点多）。
