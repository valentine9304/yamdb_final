FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT [ "/app/api_yamdb/docker-entrypoint.sh" ]
