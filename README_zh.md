# <img src="https://flog.pythonanywhere.com/static/favicon/favicon.svg" width="50px"> Flog
[英文版](./README.md)  

[![Documentation Status](https://img.shields.io/readthedocs/flog?logo=Read%20The%20Docs)](https://flog.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/z-t-y/Flog.svg?branch=master)](https://travis-ci.com/z-t-y/Flog)
[![codecov](https://codecov.io/gh/z-t-y/Flog/branch/master/graph/badge.svg?token=FZ46GGQIZ7)](https://codecov.io/gh/z-t-y/Flog)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

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

## 关于在线DEMO

本在线示例仅是Flog功能的DEMO。由于Heroku的限制，你将无法上传图片以及使用中文界面。
但是，你仍然可以体验Flog的主要功能例如聊天室、Web API和消息中心。

## API 文档

api v1 & v2
[ReadTheDocs](https://flog.readthedocs.io/en/latest/)

api v3
[Swagger文档](https://flog-web.herokuapp.com/docs)
[Redoc](https://flog-web.herokuapp.com/redoc)

## 在本地运行这个网站

### venv + pip

如果你使用venv和pip来管理虚拟环境，命令如下：

```shell
git clone https://github.com/z-t-y/Flog.git ./flog # 或git clone https://gitee.com/andyzhouty/Flog.git ./flog
cd flog/
python3 -m venv venv # 如果你使用Windows,请替换为 python -m venv venv
source ./venv/bin/activate # 如果你使用Windows，请替换为 ./venv/Scripts/activate
pip3 install -r requirements-dev.txt # 安装相关依赖
flask deploy # 初始化数据库
flask forge # 生成虚拟数据
flask create-admin
flask run
```

### Pipenv

如果你使用pipenv，命令如下：

```shell
# 克隆项目并切换到相应目录（如上）
pipenv install # 使用pipenv安装相关依赖
pipenv shell
flask deploy # 初始化数据库
flask forge
flask create-admin # 生成管理员账号
flask run
```

### Docker

Flog使用sqlite3作为Docker容器的数据库，容器关闭后数据库的所有内容会被清除。
如果不需要数据永久保存，那么放心使用，否则不推荐。

```shell
docker pull andyzhouty/flog
docker run andyzhouty/flog -d -p 5000:5000
```

### 运行单元测试

```shell
# 假设已经激活了虚拟环境
pytest
```

## Flog可选设置

| 配置名               | 默认值                       | 描述                                  |
| ------------------- | ----------------------      | ------------------------------------ |
| FLOG_EMAIL          | flog_admin@example.com      | 部署Flog时所用的邮箱（推荐使用自建服务器）  |
| FLOG_EMAIL_PASSWORD | flog_email_password         | FLOG_EMAIL的邮箱密码                   |
| FLOG_ADMIN          | flog_admin                  | Flog管理员的用户名                     |
| FLOG_ADMIN_EMAIL    | flog_admin@example.com      | Flog管理员的邮箱                       |
| FLOG_ADMIN_PASSWORD | flog_admin_password         | Flog管理员的密码                       |
| DATABASE_PROD       | sqlite:///./data.sqlite     | Flog在生产环境中的数据库URL             |
| DATABASE_DEV        | sqlite:///./data-dev.sqlite | Flog在开发环境中的数据库URL             |
| DATABASE_TEST       | sqlite:///:memory:          | Flog在单元测试中的数据库URL             |

## 关于一些小问题

1. 为什么这个项目名为'Flog'?  
   'Flog'是Flask和Blog这两个词的组合，这个词听起来（以及看起来）像'frog'，所以我用了一只青蛙作为网站的图标。

2. 为什么这个网站有时一天有好几条提交，却有时候连续几周没有提交？  
这个网站不能及时更新因为我是一名学生（作业有点多）。
