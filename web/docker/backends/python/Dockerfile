FROM python:3.11

COPY ./app /app
WORKDIR /app

RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app.py"]
