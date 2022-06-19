FROM python:3.10-alpine

RUN apk update \
 && apk add curl

WORKDIR project

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 5000
CMD [ "python", "./src/app.py"]
