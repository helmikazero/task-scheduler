FROM python:3.10-slim

RUN apt-get update && apt-get install -y cron

WORKDIR /app
COPY app /app

RUN pip install --no-cache-dir -r requirements.txt

COPY app/crontab.txt /etc/cron.d/my-cron
RUN chmod 0644 /etc/cron.d/my-cron && crontab /etc/cron.d/my-cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]
