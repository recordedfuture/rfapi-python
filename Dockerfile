FROM python:3
COPY requirements.txt /app/requirements.txt
COPY rfapi /app/rfapi
WORKDIR /app
RUN pip install -r requirements.txt
