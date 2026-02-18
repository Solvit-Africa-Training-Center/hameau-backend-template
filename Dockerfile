FROM python:3.12-slim

WORKDIR /app

RUN mkdir -p /app/logs

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

RUN chmod -R 755 /app/logs

RUN python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
