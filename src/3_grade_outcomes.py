#!/usr/bin/env python3
"""
Grades each informative outcome in the first 100 records of
abstract_extractions_copy.yaml using GPT‑4o‑mini, according to the
five‑point grading scheme provided by the user.

Output is saved to abstract_outcome_grades.yaml with entries like:
  - record_id: R00001
    term: Forest coverage
    grade: Significant

The script can be re‑run safely; completed (record_id, term) pairs will
be skipped.
"""
import os, time, yaml
from pathlib import Path
from openai import OpenAI

# ────────────── CONFIG ──────────────
# MODEL          = "gpt-4o-mini"
MODEL          = "gpt-4.1-mini" #"gpt-4.1-2025-04-14"
YAML_INPUT     = "abstract_extractions_copy.yaml"
YAML_OUTPUT    = "abstract_outcome_grades.yaml"
WAIT_TIME      = 1     # seconds between calls / retries
RETRY_LIMIT    = 3

GRADING_SCHEME = (
    "1. Very significant\n"
    "Definition: Substantial improvement in outcome, with robust evidence or clear behavioral shift; often includes statistical or numerical results.\n\n"
    "2. Significant\n"
    "Definition: Noticeable improvement in outcome, supported by qualitative or moderate quantitative evidence, but not as dramatic as \u201cvery significant.\u201d\n\n"
    "3. Neutral/mixed results\n"
    "Definition: Some improvement in outcome is suggested, but effects are limited, unclear, not statistically significant, or are offset by contradictory findings.\n\n"
    "4. No effect\n"
    "Definition: The intervention or policy had no discernible impact on outcome, as shown by the evidence.\n\n"
    "5. Outcome was worsened\n"
    "Definition: Outcome worsened or became more problematic as a result of the intervention or policy.\n"
    "If insufficient information is available to provide a grade, please respond with: No information"
)

SYSTEM_MSG = (
    "You are a careful research assistant.\n"
    "Only reply with exactly one of the following grades (no extra text):\n"
    "Very significant | Significant | Neutral/mixed results | No effect | Outcome was worsened | No information"
)

PROMPT_TMPL = (
	"Below is the grading rubric you will be using:\n"
    "{grading}\n\n"
    "This is the intervention:\n{intervention}\n\n"
    "Specific outcome of the intervention to evaluate:\n{outcome_name}\n\n"
    "Impact evaluation:\n{outcome}\n\n"
    "Assign the appropriate grade for the degree to which the outcome \"{outcome_name}\" was acheived from the intervention, based on the impact evaluation provided.\n"
    "Output exactly one of: Very significant, Significant, Neutral/mixed results, No effect, Outcome was worsened, No Information. "
)
# ─────────────────────────────────────

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- helpers ----------
def load_yaml(path: str, default):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or default
    return default

def append_yaml(path: str, item):
    mode = "a" if Path(path).exists() else "w"
    with open(path, mode, encoding="utf-8") as f:
        yaml.safe_dump([item], f, allow_unicode=True, sort_keys=False)


def is_informative(rec):
    if rec.get("kind") != "outcome":
        return False
    resp = rec.get("response", "")
    if not isinstance(resp, str):
        return False
    txt = resp.strip().lower()
    if txt in {"no information", "no information."}:
        return False
    if (
        "does not provide any information regarding" in txt
        or "does not provide specific information regarding" in txt
        or "does not provide specific information or quantitative data" in txt
        or "does not provide specific quantitative or categorical information" in txt
    ):
        return False
    return True


def ask_chatgpt(prompt: str) -> str:
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt < RETRY_LIMIT:
                time.sleep(WAIT_TIME)
            else:
                raise RuntimeError(f"OpenAI call failed after {RETRY_LIMIT} attempts: {e}")

# ---------- main ----------
def main():
    records_in  = load_yaml(YAML_INPUT, [])
    grades_out  = load_yaml(YAML_OUTPUT, [])

    done_keys = {(g["record_id"], g["term"]) for g in grades_out}

    # Build intervention lookup by record_id
    interventions = {}
    for rec in records_in:
        if rec.get("kind") == "intervention":
            interventions[rec["record_id"]] = rec.get("response", "No Intervention Described.")

    # Process first 100 records only, in file order
    to_process = records_in #[:200]

    count = 0
    for rec in to_process:
        if not is_informative(rec):
            continue
        rid  = rec["record_id"]
        term = rec["term"]
        key  = (rid, term)
        if key in done_keys:
            continue
        count += 1
        print(f"Record #{str(count)}: Grading {rid} – {term}...")
        print()

        intervention_txt = interventions.get(rid, "No Intervention Described.")
        outcome_txt      = rec["response"].strip()
        outcome_name_txt      = rec["term"].strip()

        prompt = PROMPT_TMPL.format(
            grading=GRADING_SCHEME,
            intervention=intervention_txt,
            outcome=outcome_txt,
            outcome_name=outcome_name_txt,
        )

        # import pprint
        # pprint.pprint(prompt)
        try:
            grade = ask_chatgpt(prompt)
        except RuntimeError as err:
            print(f"{rid} – {term}: {err}")
            continue

        grade = grade.strip().lower()
        print("grade")
        print(grade)
        print(type(grade))
        if grade not in {
            "very significant",
            "significant",
            "neutral/mixed results",
            "no effect",
            "outcome was worsened",
            "no information"
        }:
            print(f"Unexpected grade for {rid} – {term}: '{grade}' (saving anyway)")
        result = {
            "record_id": rid,
            "term": term,
            "grade": grade,
        }

        # grades_out.append({
        #     "record_id": rid,
        #     "term": term,
        #     "grade": grade,
        # })
        done_keys.add(key)
        append_yaml(YAML_OUTPUT, result)

        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()
