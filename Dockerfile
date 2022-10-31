FROM python:3.8.15-buster

WORKDIR /root

RUN apt-get update -y \
    && apt-get install -y build-essential git wget \
    && apt-get -y clean all

RUN pip install \
        numpy \
        deepl


