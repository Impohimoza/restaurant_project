FROM python:3.13.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        libgl1 \
        libglib2.0-0 \
        netcat-openbsd \
        && apt-get clean

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]