# start by pulling the python image
FROM python:3.8.3-slim-buster

ENV PYTHONUNBUFFERED True

# set working directory
COPY . /app
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc

RUN pip3 install -r requirements.txt

# set environment variables
ENV FLASK_APP=application.py
ENV FLASK_DEBUG=0
ENV AWS_S3_BUCKET=hubbub-marketplace
ENV BLUBBER_DEBUG=0
ENV CELERY_RESULT_BACKEND=null
ENV CORS_ALLOW_ORIGIN=https://www.hubbub.shop
ENV FLASK_ENV=production
ENV MAIL_DEFAULT_ADMIN=adb2189@columbia.edu
ENV MAIL_DEFAULT_RECEIVER=hello@hubbub.shop
ENV MAIL_DEFAULT_SENDER=hello@hubbub.shop
ENV ReCAPTCHA_SERVER_APIKEY=6Ld6vxEjAAAAALCW5Pw578wJ6eILI9YVEcq8IpF0

# secrets
ENV AWS_ACCESS_KEY_ID=AKIA3V65OEFY4RP7NW4V
ENV AWS_SECRET_ACCESS_KEY=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
ENV CLOUDAMQP_APIKEY=227ecc95-60b9-4adf-a49d-9e6447b98103
ENV CLOUDAMQP_URL=amqps://ytltevho:CT9__vh0I7NOE_XrEs3A4haVg7XXgtbx@fish.rmq.cloudamqp.com/ytltevho
ENV DATABASE_URL=postgres://rentadmin:icW3g4vvq40O0uga5gGTP0Jhbu3t2XHc@rent-production.chxjujfo7tae.us-east-1.rds.amazonaws.com:5432/rentproduction
ENV GCLOUD_ACCESS_CREDENTIALS_PRIVATE_JSON=keys/hubbub-assets-039695bfa919.json
ENV GCLOUD_ACCESS_CREDENTIALS_PRIVATE_KEY=null
ENV GCLOUD_ACCESS_CREDENTIALS_PRIVATE_KEY_ID=039695bfa919147252fe8802fbd6ac52c2eca5d3
ENV SECRET_KEY=TFqjk164fCD2HUq7xLELyMQyIw9qCdax6UDpC3H5b0
ENV SENDGRID_APIKEY=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
ENV SERVER_DOMAIN=https://rent.hubbub.shop
ENV STRIPE_APIKEY=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
ENV STRIPE_ENDPOINT_SECRET=whsec_4DuXuuZ15cJIgC1TWmiXwl0vM7LCW6hb

# configure the container to run in an executed manner
# CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "--bind", "0.0.0.0", "application:app"]
