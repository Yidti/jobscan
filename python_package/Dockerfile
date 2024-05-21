# 安裝套件

FROM apache/airflow:2.9.1

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip install --user --upgrade pip

RUN pip install -r requirements.txt
