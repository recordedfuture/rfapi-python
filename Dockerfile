FROM python:3
COPY requirements.txt rfapi/main.py /app/
COPY rfapi/*.py /app/rfapi/
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
