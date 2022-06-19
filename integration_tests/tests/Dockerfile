FROM python:3.10-slim

RUN apt-get update \
 && apt-get install -y git gcc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR project
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD [ "pytest", "-s"]
