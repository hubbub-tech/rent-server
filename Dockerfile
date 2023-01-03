# start by pulling the python image
FROM python:3.8.3-slim-buster

ENV PYTHONUNBUFFERED True

# set working directory
COPY . /app
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc

RUN pip3 install -r requirements.txt

# CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "--bind", "0.0.0.0", "application:app"]
