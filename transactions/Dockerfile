FROM python:3.11.5-slim

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app

CMD alembic -c alembic.ini upgrade head && python3 main.py
