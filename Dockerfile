FROM python:3.9

ENV PYTHONUNBUFFERED 1

ENV APP_HOME /swapper
WORKDIR $APP_HOME
COPY . ./

RUN pip install --upgrade pip
RUN pip install -r ./swapper/requirements/requirements.txt -r ./swapper/requirements/dev-requirements.txt