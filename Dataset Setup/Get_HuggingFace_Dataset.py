"""
Downloads the Amazon Reviews 2023 Electronics metadata parquet file from
Hugging Face and copies it into the project's local `data` directory.

This script retrieves the dataset file from the Hugging Face cache,
creates the target directory if necessary, and overwrites the local copy
with the latest downloaded version.
"""
from huggingface_hub import hf_hub_download
import shutil
from pathlib import Path

downloaded_path = hf_hub_download(
    repo_id="McAuley-Lab/Amazon-Reviews-2023",
    filename="raw_meta_Electronics/full-00000-of-00010.parquet",
    repo_type="dataset"
)

target_path = Path("../data/full-00000-of-00010.parquet")
target_path.parent.mkdir(exist_ok=True)

shutil.copy(downloaded_path, target_path)

print(f"Downloaded cache file: {downloaded_path}")
print(f"Copied to project: {target_path.resolve()}")