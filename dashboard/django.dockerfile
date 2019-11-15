# Start with a Python image.
FROM python:3.7-slim

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

# Install some necessary things.
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat git htop zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

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