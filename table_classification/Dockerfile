FROM python:3.13.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
        libgl1 \
        libglib2.0-0 \
        netcat-openbsd \
        dos2unix \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY entrypoint.sh /tmp/entrypoint.sh
RUN dos2unix /tmp/entrypoint.sh && \
    chmod +x /tmp/entrypoint.sh && \
    mv /tmp/entrypoint.sh /entrypoint.sh

COPY . .

RUN ls -la /entrypoint.sh && \
    head -5 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]