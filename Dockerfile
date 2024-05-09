FROM python:3.10.13-slim

# 更新 pip
RUN pip install --no-cache-dir --upgrade pip

# 安裝編譯所需的工具和庫
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "app.py"]
    