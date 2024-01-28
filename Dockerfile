FROM python:3.11-alpine

ENV APP_HOME /app

WORKDIR $APP_HOME

EXPOSE 3000

COPY . .

ENTRYPOINT [ "python3", "main.py"]