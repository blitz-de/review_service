FROM python:3.10.0-slim-buster

ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
#RUN python manage.py makemigrations
#RUN python manage.py migrate
#CMD python manage.py runserver 0.0.0.0:8000