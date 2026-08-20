FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src ./src
COPY configs ./configs
COPY scripts ./scripts

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["sh", "-c", "uvicorn ai_data_platform.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]