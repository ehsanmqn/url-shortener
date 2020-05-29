The UrlShortener project

## Table of contents

- [Requirements](#requirements)
- [Getting started](#getting-started)

## Requirements

* [RabbitMQ](https://www.rabbitmq.com/)
* [Reddis](https://redis.io/)
* [Celery](http://www.celeryproject.org/)

## Project overview

The project is a [Django](https://www.djangoproject.com/start/) application. 

## Getting started

#### Clone the repository

```bash
git clone https://gitlab.com/ehsanmqn/urlshortener
```

#### Prepare the project
```bash
cd url-shortener
virtualenv -p pyhton3 env
source env/bin/activate
pip install -r requirements.txt
```

#### Run celery worker

```bash
celery -A UrlShortener worker -l info
```

#### Run project

```bash
./manage.py runserver 8000
```

After running the project, it will be accessed through port 8000

Project API document is accessible from [here](https://documenter.getpostman.com/view/5584679/SzS5wTGQ?version=latest)
#### Happy coding!

