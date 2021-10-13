# Hubbub Shop Server

The official server for the Hubbub Shop website, hosted at https://www.hubbub.shop.

## Getting Started

Hubbub Shop is an online shop for people to rent items listed on the platform for as long as they need. This repository contains the server-side routes that authenticate users and validate transitions.

### Prerequisites

In order to run this server locally, you will need several development variables set in the run environment. These environment variables should be stored in a file called '.env.development' or '.env.production' in the './server' folder. Each variable has been described below:

*./server/.env.development*
```
export FLASK_APP=application.py
export FLASK_ENV=development
export SECRET_KEY=<some-super-secret-key>
export CORS_ALLOW_ORIGIN=<route-to-react-client>

export DATABASE_URL=<hubbub-database-url>
export BLUBBER_DEBUG=1

export CONTACT_EMAIL=<verified-hubbub-email>
export MAIL_DEFAULT_SENDER=<verified-hubbub-email>
export SENDGRID_API_KEY=<sendgrid-api-key>

export S3_BUCKET=<aws-s3-bucket-name>
export AWS_ACCESS_KEY_ID=<aws-access-id>
export AWS_SECRET_ACCESS_KEY=<aws-access-secret>

export CLOUDAMQP_URL=<worker-url>
export CELERY_BROKER_URL=<broker-url>
export CELERY_RESULT_BACKEND=<none>

export ReCAPTCHA_SERVER_API_KEY=<recaptcha-server-api-key>
```

For more information about these environment variables, visit the following resources: Flask API Docs, Blubber ORM on Github, Sendgrid by Twilio, AWS S3 File System, and Google ReCaptcha.

### Running 'Fubbub'

'Fubbub', or 'Fake Hubbub', allows you to run a copy of Hubbub locally. This is convenient for testing new features and manual debugging. Once you've cloned the server from Github run the commands below.

```
pip3 install -r requirements.txt
source server/.env.development
flask run
```

Note: while you can run the server just fine without running the client as well, you won't get the familiar GUI seen on https://www.hubbub.shop. This leaves you with two options: 1) also clone and run the client, or 2) make API calls without the GUI through a service like Postman.

### Option 1: API Calls through Postman

Download **Postman**, a service for testing API calls. This can be done simply by 1) looking up the Hubbub route that you would like to test, 2) setting your request to the proper method (GET or POST), and 3) then sending the request. All Hubbub Shop routes will respond with json and a status code. Assess these to see if the results are as expected. Contact mailto:adb2189@columbia.edu if you are running into issues.

### Option 2: Run the ReactJS client WHILE ALSO running the Flask Server

Visit https://www.github.com/hubbub-tech/shop for details on how the ReactJS client works.

## Built With

* [blubber-orm](https://www.github.com/hubbub-tech/blubber-orm) - Internal ORM for managing database queries dynamically
* [Flask Web Framework](https://www.github.com/palletsproject/flask) - Python web development framework

## Contributing

Hubbub is currently not taking contributions. This policy may change in the future.

## Authors

* **Ade Balogun** - *Initial work* - [Baloguna16](https://github.com/Baloguna16)
