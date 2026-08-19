from __future__ import annotations

import argparse
import json

from ai_data_platform.config import load_settings
from ai_data_platform.pipeline import run_pipeline
from ai_data_platform.utils.logging import configure_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI data infrastructure pipeline")
    parser.add_argument("--config", default="configs/pipeline.yml")
    args = parser.parse_args()

    configure_logging()
    settings = load_settings(args.config)
    result = run_pipeline(settings)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
