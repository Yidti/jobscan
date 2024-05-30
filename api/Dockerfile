FROM python:3.10.14-alpine

WORKDIR /api

COPY ./requirements.txt /api/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

#COPY main.py /api/

# reload 可以即時更新
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888", "--reload"]