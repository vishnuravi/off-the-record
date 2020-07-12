FROM python:3.6
ADD . /off-the-record
WORKDIR /off-the-record
RUN pip install -r requirements.txt