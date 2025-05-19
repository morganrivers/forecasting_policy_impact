#!/usr/bin/env python3
import yaml
from collections import Counter, defaultdict
from pathlib import Path

YAML_PATH = "../data/abstract_extractions.yaml"

def load_yaml(path):
    if not Path(path).exists():
        print(f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def is_informative(rec):
    # Only consider records with kind == "outcome"
    if rec.get("kind") != "outcome":
        return False
    if rec["response"].strip().lower() == "no information" \
        or rec["response"].strip().lower() == "no information."\
        or "does not provide any information regarding" in rec["response"].strip().lower()\
        or "does not provide specific information regarding" in rec["response"].strip().lower()\
        or "does not provide specific information or quantitative data" in rec["response"].strip().lower()\
        or "does not provide specific quantitative or categorical information" in rec["response"].strip().lower():
        return False
    return True

def main():
    records = load_yaml(YAML_PATH)

    outcome_records = [r for r in records if is_informative(r)]

    # Count occurrences of each outcome term
    term_counter = Counter(r["term"] for r in outcome_records)

    # Group records by term
    grouped = defaultdict(list)
    for r in outcome_records:
        grouped[r["term"]].append(r)

    # Sort terms by frequency (descending)
    sorted_terms = sorted(term_counter.items(), key=lambda x: -x[1])

    for term, count in sorted_terms:
        if count <= 4:
            continue
        print("=" * 80)
        print(f"Outcome: {term} ({count} occurrences)")
        print("-" * 80)

        for rec in grouped[term]:
            if(is_informative(rec)):
                print(f"Record ID: {rec['record_id']}")
                # print("Abstract:")
                # print(rec["abstract"].strip())
                print("Response:")
                print(rec["response"].strip())
                print("-" * 80)

if __name__ == "__main__":
    main()
