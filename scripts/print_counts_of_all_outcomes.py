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

def main():
    records = load_yaml(YAML_PATH)

    # Filter only outcome-type records
    outcome_records = [r for r in records if r.get("kind") == "outcome"]
    total_outcomes = len(outcome_records)

    no_info_count = 0
    informative_count = 0
    per_term_counts = defaultdict(int)
    unique_record_ids = set()

    for r in outcome_records:
        record_id = r.get("record_id")
        if record_id:
            unique_record_ids.add(record_id)
        response = r.get("response", "").strip().lower()
        if response == "no information." or response == "no information":
            no_info_count += 1
        else:
            informative_count += 1
            per_term_counts[r["term"]] += 1

    print("=" * 80)
    print(f"Total unique record IDs: {len(unique_record_ids)}")
    print(f"Total outcomes: {total_outcomes}")
    print(f"Outcomes with 'No Information': {no_info_count}")
    print(f"Fraction with 'No Information': {no_info_count / total_outcomes:.2%}")
    print(f"Total informative outcomes: {informative_count}")
    print("=" * 80)
    at_least_3_informative = sum(1 for count in per_term_counts.values() if count >= 3)
    print(f"Number of outcome terms with at least 3 informative responses: {at_least_3_informative}")
    print(f"Number of informative responses terms from outcomes with at least 3 informative responses: {at_least_3_informative}")
    informative_from_terms_with_3_plus = sum(count for count in per_term_counts.values() if count >= 3)
    print(f"Number of informative responses from outcomes with at least 3 informative responses: {informative_from_terms_with_3_plus}")
    print("Informative outcome counts by term:")
    for term, count in sorted(per_term_counts.items(), key=lambda x: -x[1]):
        print(f"{term}: {count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
