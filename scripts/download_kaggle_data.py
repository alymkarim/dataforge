from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


DATASETS = {
    "ecommerce": {
        "slug": "mkechinov/ecommerce-behavior-data-from-multi-category-store",
        "output": "data/raw/ecommerce",
    },
}


def download_dataset(dataset_name: str) -> None:
    if dataset_name not in DATASETS:
        available = ", ".join(DATASETS)
        raise ValueError(
            f"Unknown dataset '{dataset_name}'. "
            f"Available datasets: {available}"
        )

    dataset = DATASETS[dataset_name]

    output_dir = Path(dataset["output"])
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        dataset["slug"],
        "-p",
        str(output_dir),
        "--unzip",
    ]

    print(f"Downloading {dataset_name}...")
    print(f"Kaggle dataset: {dataset['slug']}")
    print(f"Destination: {output_dir}")

    subprocess.run(command, check=True)

    print()
    print("Download complete.")

    files = list(output_dir.iterdir())

    if files:
        print("\nFiles:")
        for file in files:
            print(f" - {file.name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download datasets from Kaggle."
    )

    parser.add_argument(
        "--dataset",
        required=True,
        choices=DATASETS.keys(),
        help="Dataset to download.",
    )

    args = parser.parse_args()

    download_dataset(args.dataset)


if __name__ == "__main__":
    main()