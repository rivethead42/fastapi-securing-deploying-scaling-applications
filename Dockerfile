FROM python:3.11-slim

WORKDIR /app

ENV MONGO_URI mongodb://localhost:27017
ENV MONGO_DB_NAME widget_db
ENV REDIS_URI redis://localhost:6379/0
ENV REDIS_TTL 3600
ENV SECRET_KEY your-secret-key-please-change-in-production
ENV ALGORITHM HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES 30
ENV CORS_ALLOW_ORIGINS http://localhost,http://localhost:3000,https://yourdomain.com
ENV RATE_LIMIT_ANON_REQUESTS 30
ENV RATE_LIMIT_AUTH_REQUESTS 100
ENV RATE_LIMIT_WINDOW_SECONDS 60

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]