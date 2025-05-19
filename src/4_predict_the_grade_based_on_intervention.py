#!/usr/bin/env python3
"""
Forecasts the *expected* grade for each informative outcome using
GPT‑4.1‑2025‑04‑14 **before** reading the outcome description.

Prompt provides only the intervention text and the name of the outcome.
The model must respond with three labelled sections **in this exact
order**:

Scratchpad thoughts: free‑form step‑by‑step reasoning
Prediction: 1‑3 sentence qualitative forecast of the outcome direction
Grade: one of → Very significant | Significant | Neutral/mixed results |
       No effect | Outcome was worsened | No information

Each result is appended immediately to `abstract_outcome_forecasts.yaml`
so the script can resume safely after interruption.
"""
import os, time, yaml
from pathlib import Path
from openai import OpenAI

# ────────────── CONFIG ──────────────
MODEL          = "gpt-4.1-2025-04-14"
YAML_INPUT     = "abstract_extractions_copy.yaml"
YAML_OUTPUT    = "abstract_outcome_forecasts.yaml"
WAIT_TIME      = 1      # seconds between calls / retries
RETRY_LIMIT    = 3

RUBRIC = (
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
)

SYSTEM_MSG = (
    "You are a disciplined forecasting assistant.\n"
    "Deliberate internally but output exactly three labelled sections in this order:\n"
    "Scratchpad thoughts: <your step‑by‑step reasoning>\n"
    "Prediction: <1‑3 sentences>\n"
    "Grade: <Very significant | Significant | Neutral/mixed results | No effect | Outcome was worsened | No information>"
)

PROMPT_TMPL = (
    "Grading rubric:\n{rubric}\n\n"
    "Intervention description:\n{intervention}\n\n"
    "Outcome to evaluate:\n{outcome}\n\n"
    "Using only the information above plus your world knowledge, forecast the most likely grade.\n"
    "Think through causal pathways, historical base‑rates, and similar programs. Weigh arguments for each grade, then decide the single most likely grade.\n"
    "Respond with the three labelled sections:"
    "Scratchpad thoughts: <your step‑by‑step reasoning>\n"
    "Prediction: <1‑3 sentences>\n"
    "Grade: <Very significant | Significant | Neutral/mixed results | No effect | Outcome was worsened | No information>"

)

VALID_GRADES = {
    "very significant",
    "significant",
    "neutral/mixed results",
    "no effect",
    "outcome was worsened",
    "no information",
}

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
    existing    = load_yaml(YAML_OUTPUT, [])

    done_keys = {(r["record_id"], r["term"]) for r in existing}

    # Map record_id -> intervention text
    interventions = {
        rec["record_id"]: rec.get("response", "No Intervention Described.")
        for rec in records_in if rec.get("kind") == "intervention"
    }

    count = 0
    for rec in records_in[:500]:
        if not is_informative(rec):
            continue
        rid, term = rec["record_id"], rec["term"]
        if (rid, term) in done_keys:
            continue

        count += 1
        print(f"[{count}] Forecasting {rid} – {term}…")

        prompt = PROMPT_TMPL.format(
            rubric=RUBRIC,
            intervention=interventions.get(rid, "No Intervention Described."),
            outcome=term,
        )
        # import pprint
        # pprint.pprint(prompt)

        try:
            reply = ask_chatgpt(prompt)
        except RuntimeError as err:
            print(f"{rid} – {term}: {err}")
            continue

        # Expect three labelled lines; tolerate multi‑line scratchpad
        scratchpad, prediction, grade = "", "", ""
        lines = [l.strip() for l in reply.splitlines() if l.strip()]
        section = None
        for line in lines:
            low = line.lower()
            if low.startswith("scratchpad thoughts"):
                section = "scratchpad"
                scratchpad = line.split(":",1)[1].strip()
            elif low.startswith("prediction"):
                section = "prediction"
                prediction = line.split(":",1)[1].strip()
            elif low.startswith("grade"):
                section = "grade"
                grade = line.split(":",1)[1].strip().lower()
            else:
                if section == "scratchpad":
                    scratchpad += (" " if scratchpad else "") + line
                elif section == "prediction":
                    prediction += (" " if prediction else "") + line
        if grade not in VALID_GRADES:
            print(f"{rid} – {term}: unexpected grade '{grade}', saving anyway")

        record = {
            "record_id": rid,
            "term": term,
            "scratchpad": scratchpad,
            "prediction": prediction,
            "grade": grade,
        }
        append_yaml(YAML_OUTPUT, record)
        done_keys.add((rid, term))
        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    main()
