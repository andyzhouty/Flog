FROM python:3.9-slim

WORKDIR /usr/src/flog/

COPY Pipfile* ./
RUN pip install pipenv -i https://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
RUN pipenv install --system --deploy

COPY flog/ flog/
COPY migrations/ migrations/
COPY wsgi.py ./
COPY docker_boot.sh ./
COPY tests/ tests/
RUN chmod +x docker_boot.sh

ENV FLASK_APP wsgi.py

EXPOSE 5000
ENTRYPOINT ["./docker_boot.sh"]
