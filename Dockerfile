FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY scripts ./scripts
RUN pip install --no-cache-dir .
CMD ["ai-data-pipeline", "--config", "configs/pipeline.yml"]
