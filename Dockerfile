FROM python:3.10-slim
 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
 
WORKDIR /app
 
RUN apt-get update && apt-get install -y \
    build-essential gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    redis-server \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
EXPOSE 8000
EXPOSE 6379
 
CMD ["sh", "-c", "redis-server & celery -A whatsapp_integration  worker --loglevel=info --pool=solo  & python3 manage.py runserver 0.0.0.0:8000"]