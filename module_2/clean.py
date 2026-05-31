import json
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent

RAW_FILE = MODULE_DIR / "applicant_data.json"
LLM_INPUT_FILE = MODULE_DIR / "applicant_data_for_llm.json"
BATCH_DIR = MODULE_DIR / "llm_batches"
FINAL_OUTPUT_FILE = MODULE_DIR / "llm_extend_applicant_data.json"


def prepare_llm_input():
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    converted = []

    for row in data:
        new_row = row.copy()

        program_name = row.get("program_name") or ""
        university = row.get("university") or ""

        new_row["program"] = f"{program_name}, {university}"

        converted.append(new_row)

    with open(LLM_INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    print(f"Created {LLM_INPUT_FILE}")
    print(f"Records prepared: {len(converted)}")


def convert_jsonl_to_json():
    cleaned_records = []
    batch_files = sorted(BATCH_DIR.glob("batch_*.jsonl"))
    print(f"Found {len(batch_files)} batch files.")
    for batch_file in batch_files:
        print(f"Reading {batch_file.name}")

        with open(batch_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cleaned_records.append(json.loads(line))

    with open(FINAL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

    print(f"Created {FINAL_OUTPUT_FILE}")
    print(f"Cleaned records: {len(cleaned_records)}")

def clean_data():
    prepare_llm_input()
    convert_jsonl_to_json()

if __name__ == "__main__":
    clean_data()