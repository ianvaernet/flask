FROM python:3.9-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
COPY .env /usr/src/app/

RUN apk add build-base mariadb-connector-c-dev libffi-dev

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 80

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]
