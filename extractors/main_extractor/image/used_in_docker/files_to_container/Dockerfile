FROM python:3.6.3

ADD requirements.txt /test/requirements.txt
WORKDIR /test

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt


ADD . /test

EXPOSE 80

ENV NAME World