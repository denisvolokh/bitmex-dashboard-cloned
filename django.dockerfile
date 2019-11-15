# Start with a Python image.
FROM python:3.7-slim

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

# Install some necessary things.
RUN apt-get update
RUN apt-get update
RUN apt-get update
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat git htop
# RUN apt-get install -y python3.7-dev gcc
RUN apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev libxslt-dev gcc

# Copy all our files into the image.
RUN mkdir /code
WORKDIR /code
COPY . /code/

EXPOSE 5000

# Install our requirements.
RUN pip install -U pip
RUN pip install pipenv
RUN pipenv install --system

RUN env

CMD ["python", "manage.py", "runserver"]