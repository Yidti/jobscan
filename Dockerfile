# 安裝套件

FROM apache/airflow:2.9.1

# 安装所需的 Python 包
ADD requirements.txt .

RUN pip install -r requirements.txt

# ENV CHROME_DRIVER_PATH=/usr/bin/chromedriver
