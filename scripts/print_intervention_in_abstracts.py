#!/usr/bin/env python3
"""
Print the intervention description alongside the abstract for every record.

Works with:
 • extraction YAMLs (records have "kind": "intervention" and "response")
 • raw impact_records.yaml (records have an "interventions" list)
"""
import sys, yaml
from pathlib import Path
from textwrap import fill

DEFAULT_YAML = "../data/impact_records.yaml"

def load_yaml(path):
    if not Path(path).exists():
        sys.exit(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def main(path):
    records = load_yaml(path)

    selected = []
    for rec in records:
        if not isinstance(rec, dict):
            continue

        # style 1: extraction rows
        if rec.get("kind") in {"intervention", "intervention_summary"}:
            selected.append({
                "id":        rec.get("record_id", "—"),
                "title":     rec.get("title", "—"),
                "year":      rec.get("year_of_publication", "—"),
                "abstract":  rec.get("abstract", "").strip() or "—",
                "intervention": rec.get("response", "").strip() or "—",
            })
        # style 2: raw catalogue rows
        elif rec.get("interventions"):
            selected.append({
                "id":        rec.get("id", "—"),
                "title":     rec.get("title", "—"),
                "year":      rec.get("year_of_publication", "—"),
                "abstract":  (rec.get("abstract") or "").strip() or "—",
                "intervention": "; ".join(rec.get("interventions", [])) or "—",
            })

    if not selected:
        sys.exit("No intervention records found.")

    for item in selected:
        print("="*80)
        print(f"Record ID : {item['id']}")
        print(f"Title     : {item['title']}")
        print(f"Year      : {item['year']}")
        print("-"*80)
        print("Abstract:")
        print(fill(item["abstract"], width=90))
        print("\nIntervention Description:")
        print(fill(item["intervention"], width=90))
        print()

if __name__ == "__main__":
    yaml_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_YAML
    main(yaml_path)
