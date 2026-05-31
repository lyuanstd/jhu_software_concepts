import subprocess
import time
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
LLM_DIR = MODULE_DIR / "llm_hosting"
BATCH_DIR = MODULE_DIR / "llm_batches"

PYTHON_COMMAND = "python"


def count_jsonl_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def run_one_batch(batch_file):
    output_file = batch_file.with_suffix(".jsonl")

    if output_file.exists():
        line_count = count_jsonl_lines(output_file)

        if line_count > 0:
            print(f"Skipping {output_file.name}: already exists with {line_count} lines.")
            return

    print(f"\nRunning LLM cleaner for {batch_file.name}...")
    start_time = time.time()

    subprocess.run(
        [
            PYTHON_COMMAND,
            "app.py",
            "--file",
            str(batch_file),
            "--out",
            str(output_file),
        ],
        cwd=LLM_DIR,
        check=True,
    )

    elapsed = time.time() - start_time
    line_count = count_jsonl_lines(output_file)

    print(f"Finished {output_file.name}")
    print(f"Lines written: {line_count}")
    print(f"Elapsed time: {elapsed / 60:.2f} minutes")


def main():
    batch_files = sorted(BATCH_DIR.glob("batch_*.json"))

    if not batch_files:
        print("No batch files found.")
        return

    print(f"Found {len(batch_files)} batch files.")

    for batch_file in batch_files:
        run_one_batch(batch_file)

    print("\nAll available batches are processed.")


if __name__ == "__main__":
    main()