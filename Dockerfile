# minimalny linux z pythonem
FROM python:3.11-alpine 

ENV APP_HOME /app

WORKDIR $APP_HOME

EXPOSE 3000

COPY . .

#ENTRYPOINT [ "flask", "--app", "app.py", "run"]
ENTRYPOINT [ "python3", "main.py"]