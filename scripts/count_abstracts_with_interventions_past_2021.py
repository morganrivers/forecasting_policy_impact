#!/usr/bin/env python3
import re
import yaml
from pathlib import Path
import statistics
import matplotlib.pyplot as plt

# ======== Constants ========
YAML_PATH = "../data/impact_records.yaml"
YEAR_REGEX = re.compile(r"\b(19[6-9]\d|20[0-4]\d|2050)\b")

# ======== Helper Functions ========

def load_yaml(path):
    if not Path(path).exists():
        print(f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def find_years_with_context(text, radius=40):
    matches = []
    for match in YEAR_REGEX.finditer(text):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        context = text[start:end].replace('\n', ' ')
        matches.append((int(match.group()), context))
    return matches

def is_excludable_year_mention(text: str, year: int) -> bool:
    """
    Returns True if the year is part of a known copyright/publisher-style phrase.
    """
    year_str = str(year)
    patterns = [
        f"(c) {year_str}",
        f"© {year_str}",
        f"{year_str} elsevier",
        f"{year_str} the authors",
        f"{year_str} western social science",
        f"{year_str} wiley",
        f"{year_str} taylor & francis",
        f"{year_str} springer",
        f"{year_str} sage",
        f"{year_str} oxford university press",
        f"{year_str} academic press",
    ]
    text_lower = text.lower()
    return any(pat in text_lower for pat in patterns)

# ======== Main Script ========

def main():
    records = load_yaml(YAML_PATH)
    print(f"Loaded {len(records)} records")

    diffs = []
    valid_records = 0
    eligible_records = 0
    valid_records_with_context = []

    for rec in records:
        if rec:
            pub_year = rec.get("year_of_publication")
            abstract = rec.get("abstract", "")
            if not pub_year or not abstract:
                continue

            try:
                pub_year_int = int(pub_year)
            except ValueError:
                continue
            eligible_records += 1

            matches = [
                (y, ctx) for (y, ctx) in find_years_with_context(abstract)
                if not is_excludable_year_mention(abstract, y)
            ]

            if not matches:
                continue

            mentioned_years = {year for year, _ in matches}
            if not mentioned_years:
                continue

            # if pub_year_int in mentioned_years or any(y <= pub_year_int - 4 for y in mentioned_years):
            if any(y <= pub_year_int - 4 for y in mentioned_years):
                continue

            # if mentioned_years.issubset({pub_year_int - 1, pub_year_int - 2, pub_year_int - 3}):
            if mentioned_years.issubset({pub_year_int - 1, pub_year_int - 2, pub_year_int - 3}):
                valid_records += 1
                valid_records_with_context.append((pub_year_int, rec, matches))


            # Collect all year gaps for histogram
            for mentioned_year in mentioned_years:
                diffs.append(pub_year_int - mentioned_year)

    # ====== Stats and Output ======
    print("\n" + "=" * 80)
    if eligible_records > 0:
        print("valid_records")
        print(valid_records)
        print("eligible_records")
        print(eligible_records)
        pct = 100 * valid_records / eligible_records
        print(f"{pct:.2f}% of eligible records mention only years 1–3 years before publication.")
    else:
        print("No eligible records for year-range analysis.")

    if diffs:
        print("\nYear Mention Gap Statistics:")
        print(f"Mean difference (all mentions): {statistics.mean(diffs):.2f} years")
        print(f"Median difference (all mentions): {statistics.median(diffs):.2f} years")
        pos_diffs = [d for d in diffs if d >= 0]
        if pos_diffs:
            print(f"Mean difference (non-negative): {statistics.mean(pos_diffs):.2f} years")
            print(f"Median difference (non-negative): {statistics.median(pos_diffs):.2f} years")

    else:
        print("No valid year differences found.")

    # ====== Context Printouts ======
    print("\n" + "=" * 80)
    print("Valid eligible records with 1–3 year gap and context:")
    for i, (pub_year, rec, matches) in enumerate(valid_records_with_context, 1):
        print(f"\nRecord {i} (Publication year: {pub_year}):")
        for year, context in matches:
            print(f"  Mentioned year {year}: ...{context}...")

    print("\n" + "=" * 80)
    if diffs:


        plt.figure()
        plt.hist(diffs, bins=30)
        plt.xlabel("Publication year – Mentioned year (years)")
        plt.ylabel("Frequency")
        plt.title("Histogram of time gap between intervention and publication")
        plt.tight_layout()
        plt.show()
# ======== Entry Point ========
if __name__ == "__main__":
    main()
