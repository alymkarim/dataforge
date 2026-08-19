.PHONY: install sample run test lint clean docker

install:
	python -m pip install -e ".[dev]"

sample:
	python scripts/generate_sample_data.py --rows 5000

run:
	ai-data-pipeline --config configs/pipeline.yml

test:
	pytest --cov=ai_data_platform --cov-report=term-missing

lint:
	ruff check src tests scripts

clean:
	rm -rf data/bronze/* data/silver/* data/gold/* data/quarantine data/pipeline_metrics.jsonl

docker:
	docker compose up --build
