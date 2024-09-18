FROM python:3.11-bullseye

WORKDIR /app

RUN pip install playwright==1.46.0 && playwright install-deps && playwright install

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
