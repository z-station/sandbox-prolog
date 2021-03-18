FROM python:3.8

RUN apt-get update && \
    apt-get -y install nano && \
    pip install --upgrade pip && \
    pip install pipenv

COPY ./src/Pipfile ./src/Pipfile.lock /tmp/
RUN cd /tmp && pipenv install --deploy --system

WORKDIR /app/src
ENTRYPOINT ["./start.sh"]
# CMD tail -f /dev/null