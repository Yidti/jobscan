FROM python:3.10.13-slim

WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
