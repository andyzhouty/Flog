FROM python:3.8

WORKDIR /usr/src/flog/

COPY requirements/ requirements/
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN pip install -r requirements/common.txt
RUN pip install gunicorn

COPY flog/ flog/
COPY migrations/ migrations/
COPY wsgi.py ./
COPY docker_boot.sh ./
RUN chmod +x docker_boot.sh

ENV FLASK_APP wsgi.py

EXPOSE 5000
ENTRYPOINT ["./docker_boot.sh"]
