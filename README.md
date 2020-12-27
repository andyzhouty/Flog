# <img src="https://flog.pythonanywhere.com/static/favicon/favicon.svg" width="50px"> Flog
[中文版 README](./README_zh.md)   
[![Documentation Status](https://img.shields.io/readthedocs/flog?logo=Read%20The%20Docs&style=for-the-badge)](https://flog.readthedocs.io/en/latest/?badge=latest)
[![CircleCI Status](https://img.shields.io/circleci/build/github/z-t-y/Flog?logo=circleci&style=for-the-badge)](https://circleci.com/gh/z-t-y/Flog)
[![Coverage Status](https://img.shields.io/coveralls/github/z-t-y/Flog?logo=coveralls&style=for-the-badge)](https://coveralls.io/github/z-t-y/Flog?branch=master)


Icons made by
[Freepik]("https://www.flaticon.com/authors/freepik") from
[www.flaticon.com](www.flaticon.com)

The blog website created during learning flask.  

## Contributors

[Andy Zhou on Github](https://github.com/z-t-y "ZTY")

## Thanks To

### Projects

- [Flask](https://github.com/pallets/flask)
- [Bootstrap](https://github.com/twbs/bootstrap)
- [Bootstrap-Flask](https://github.com/greyli/bootstrap-flask)
- [Flask-WTF](https://github.com/lepture/flask-wtf)

### Books

- [Python Web Development with Flask by GreyLi](https://helloflask.com)  
- [Flask Web Development by Miguel Grinberg](https://www.oreilly.com/library/view/flask-web-development/9781491991725/)

### People

- [GreyLi](https://greyli.com)

Without these projects, the website cannot be developed.  
At the same time, thanks to [GreyLi](https://greyli.com), it was his _Python Web Development with Flask_
that took me into the wonderful world of Flask.

## Functions

- Login / Register (requires email verification) / Logout / Delete Account
- Collect  
- Follow  
- Write  
- Comment  
- Notifications
- Two languages support (zh_CN and en_US)  
- Web API

## Web API Documents

[ReadTheDocs](https://flog.readthedocs.io/en/latest/)

## Run Flog locally

### Run the website

If you prefer to use pip + requirements.txt, then:

```shell
git clone https://github.com/z-t-y/Flog.git ./flog
cd flog/
python3 -m venv venv # or `python -m venv venv` on windows
source ./venv/bin/activate # or `./venv/Scripts/activate` on windows
pip3 install -r requirements.txt
flask forge # generates fake data
flask create-admin
flask run
```

Or if you prefer to use pipenv, then:

```shell
# clone the project and change to that directory
pipenv install
pipenv shell
flask forge # generates fake data
flask create-admin
flask run
```

The default settings for the app:

| Name          |  FLOG_EMAIL | FLOG_EMAIL_PASSWORD | FLOG_ADMIN | FLOG_ADMIN_EMAIL | FLOG_ADMIN_PASSWORD |
| ---           | ----------- | ------------------- | ---------- | ---------------- | ------------------- |
| Default Value | flog_admin@example.com | flog_email_password | flog_admin | flog_admin@example.com | flog_admin_password |
| Description   | the email address used for deploying flog | the password for `FLOG_EMAIL` | the username for the administrator of flog | the administrator's email address | the administrator's password

### Run the unittests

pip+requirements.txt

```shell
source ./venv/bin/activate # or `./venv/Scripts/activate` on windows
pip3 install -r requirements-dev.txt
flask test
```

pipenv

```shell
pipenv install --dev
pipenv shell
pytest
```

Note:
If the `test_push_notification` test failed to run and the error message is like:

```text
sqlite3.InterfaceError Error binding parameter 0.
```

It should be caused by sqlite3 and you should set another database in env variable `DATABASE_TEST` for unittesting such as mysql or postgresql.


## FAQ

1. Q: Why 'Flog'?  
A: 'Flog' is a combination of 'Flask' and 'Blog'. The word sounds (and looks) like 'frog'. So I use a frog as its icon.

2. Q: Why can't the website be updated frequently?  
The website cannot be updated on time because I'm a student in Middle School now. There is much homework.
