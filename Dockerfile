FROM python:3.9-slim

WORKDIR /usr/src/flog/

COPY Pipfile* ./
RUN pip install pipenv -i https://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
RUN pipenv install --dev --system --deploy

COPY flog/ flog/
COPY migrations/ migrations/
COPY wsgi.py ./
COPY tests/ tests/
COPY scripts/ scripts/
RUN chmod +x scripts/docker_boot.sh

ENV FLASK_APP wsgi.py

EXPOSE 5000

LABEL com.circleci.preserve-entrypoint=true
ENTRYPOINT ["scripts/docker_boot.sh"]
