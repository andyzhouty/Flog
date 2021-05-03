# <img src="https://flog.pythonanywhere.com/static/favicon/favicon.svg" width="50px"> Flog
[中文版 README](./README_zh.md)

[![Documentation Status](https://img.shields.io/readthedocs/flog?logo=Read%20The%20Docs)](https://flog.readthedocs.io/en/latest/?badge=latest)
[![CircleCI Status](https://img.shields.io/circleci/build/gh/z-t-y/Flog?label=circleci&logo=circleci)](https://circleci.com/gh/z-t-y/Flog)
[![Coverage Status](https://img.shields.io/coveralls/github/z-t-y/Flog?logo=coveralls)](https://coveralls.io/github/z-t-y/Flog?branch=master)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

Icons made by
[Freepik]("https://www.flaticon.com/authors/freepik") from
[www.flaticon.com](www.flaticon.com)

The blog website is created when I'm learning flask.

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

## Plans

I'm currently planning to add access tokens and refresh tokens to api v3.
It might use flask-apispec and flask-jwt-extended.

## Web API Documents

[ReadTheDocs](https://flog.readthedocs.io/en/latest/)

## Run Flog locally

### venv + pip

If you prefer to use pip + requirements.txt, then:

```shell
git clone https://github.com/z-t-y/Flog.git ./flog
cd flog/
python3 -m venv venv # or `python -m venv venv` on windows
source ./venv/bin/activate # or `./venv/Scripts/activate` on windows
pip3 install -r requirements/dev.txt
flask deploy # initialize database
flask forge # generates fake data
flask create-admin
flask run
```

### pipenv

Or if you prefer to use pipenv, then:

```shell
# clone the project and change to that directory
pipenv install --dev --pre
pipenv shell
flask deploy # initialize database
flask forge # generates fake data
flask create-admin
flask run
```

### Docker

Note that Flog uses sqlite3 as the database for the docker container and that means
the data cannot be stored forever.

```shell
docker pull andyzhouty/flog
docker run andyzhouty/flog -d -p 5000:5000
```

### Unittests

```shell
# activate the virtual environment
pytest # or `pipenv run pytest`
```

## Available Settings for Flog

| Config Name         | Default Value          | Description                                |
| ------------------- | ---------------------- | ------------------------------------------ |
| FLOG_EMAIL          | flog_admin@example.com | The email address used for deploying flog. |
| FLOG_EMAIL_PASSWORD | flog_email_password    | The email password for FLOG_EMAIL          |
| FLOG_ADMIN          | flog_admin             | The username of the administrator of flog. |
| FLOG_ADMIN_EMAIL    | flog_admin@example.com | The administrator's email address.         |
| FLOG_ADMIN_PASSWORD | flog_admin_password    | The administrator's password.              |

## FAQ

1. Q: Why 'Flog'?  
A: 'Flog' is a combination of 'Flask' and 'Blog'. The word sounds (and looks) like 'frog'. So I use a frog as its icon.

2. Q: Why can't the website be updated frequently?  
The website cannot be updated on time because I'm a student in Middle School now. There is much homework.
