FROM python:3-slim-stretch

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && mkdir /app

WORKDIR /app/

COPY group-sync.py \
    requirements.txt \
    logging.yml \
    ./
COPY sync_target ./sync_target

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "group-sync.py"]
