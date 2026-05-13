FROM python:3.12-slim
WORKDIR /app

# Опционально: увеличиваем тайм-аут и количество попыток
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=5

COPY requirements.txt .

# Используем зеркало Яндекса
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]