#!/usr/bin/env python3
"""
Incrementally extracts what each abstract says about every outcome and interventions
term in impact_records.yaml.  Results are stored (and re-loaded) in
abstract_extractions.yaml so the script can resume after an interruption.

Each record in the output YAML has:
  record_id   – “R00001”, “R00002”, …
  kind        – “outcome” or “interventions”
  term        – the term being queried
  query       – full prompt sent to GPT-4o-mini
  abstract    – the abstract text
  response    – GPT-4o-mini’s full answer
"""
import os, time, yaml
from pathlib import Path
from openai import OpenAI
import pprint
# ────────────── CONFIG ──────────────
MODEL          = "gpt-4.1-mini" #"gpt-4.1-2025-04-14"
YAML_INPUT     = "impact_records.yaml"
YAML_OUTPUT    = "abstract_extractions.yaml"
WAIT_TIME      = 1          # seconds between calls / retries
RETRY_LIMIT    = 3

QUESTION_TMPL_INTERVENTION = (
    "What is the intervention that is described in the abstract? "
    "This is an abstract for an impact evaluation report about an intervention in a developing country. "
    "The intervention has been categorized as follows: \"{intervention_list}\". "
    "Do not mention the outcomes or analysis method, only describe the intervention with as much detail as is present in the abstract. "
    "Ensure to include any contextual information about what was done and where in your response. "
    "If nothing is said about the intervention write: No Intervention Described."
)

QUESTION_TMPL_OUTCOME = (
    "What does the abstract say regarding the \"{term}\" outcome? "
    "Be sure to include relevant quantitative or categorical information where present. "
    "If nothing is said about the outcome write: No Information."
)

SYSTEM_MSG = (
    "You are analysing paper abstracts. "
    "Return only the answer text (no numbering, no extra commentary)."
)
# ─────────────────────────────────────

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- helpers ----------
def load_yaml(path: str, default):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or default
    return default

def save_yaml(path: str, data):
    tmp = Path(path).with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    tmp.replace(path)

def ask_chatgpt(prompt: str) -> str:
    for attempt in range(1, RETRY_LIMIT + 1):
        print("asking...")
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user",   "content": prompt}
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
    input_records  = load_yaml(YAML_INPUT,  [])
    output_records = load_yaml(YAML_OUTPUT, [])

    processed_keys = {
        (r["record_id"], r["kind"], r["term"]) for r in output_records
    }

    count = 0
    for idx, rec in enumerate(input_records, start=1):
        if not isinstance(rec, dict):
            print(f"Skipping invalid record at idx={idx}: {rec}")
            continue

        print("idx")
        print(idx)

        count += 1
        # if count >= 10:
        #     break

        rec_id   = f"R{idx:05}"
        abstract = rec.get("abstract")
        if not isinstance(abstract, str):
            print(f"Missing or invalid abstract for record {rec.get('record_id', idx)}")
            continue
        abstract = abstract.strip()

        # outcomes and interventions may be stored under different field names
        outcomes      = rec.get("outcome", []) or []
        interventions   = rec.get("interventions", []) or []
        intervention_list = ", ".join(interventions)
        # Now handle interventions (one prompt total)
        

        for kind, terms in (("outcome", outcomes), ("intervention", [intervention_list])):
            if kind == "intervention":
                term = "intervention"
                key = (rec_id, kind, term)

                if key in processed_keys:
                    continue  # already done in a previous run

                prompt = (
                    f"{QUESTION_TMPL_INTERVENTION.format(intervention_list=intervention_list)}\n\n"
                    f"Abstract:\n\"\"\"\n{abstract}\n\"\"\""
                )
                print("")
                print("")
                print(f"{rec_id} – {kind} – '{term}'")
                print("")

                # print(prompt)
                # pprint.pprint(prompt)
                try:
                    answer = ask_chatgpt(prompt)
                except RuntimeError as err:
                    print(f"{rec_id} – {kind} – '{term}': {err}")
                    continue
                # answer = "DUMMY DELETEME"
                output_records.append({
                    "record_id": rec_id,
                    "kind":      kind,
                    "term":      term,
                    "query":     prompt,
                    "abstract":  abstract,
                    "response":  answer,
                })
                processed_keys.add(key)
                save_yaml(YAML_OUTPUT, output_records)
                time.sleep(WAIT_TIME)
            else:
                for term in terms:
                    key = (rec_id, kind, term)


                    if key in processed_keys:
                        continue  # already done in a previous run

                    prompt = (
                        f"{QUESTION_TMPL_OUTCOME.format(term=term)}\n\n"
                        f"Abstract:\n\"\"\"\n{abstract}\n\"\"\""
                    )

                    print("")
                    print("")
                    print(f"{rec_id} – {kind} – '{term}'")
                    print("")
                    # print(prompt)
                    # pprint.pprint(prompt)
                    try:
                        answer = ask_chatgpt(prompt)
                    except RuntimeError as err:
                        print(f"{rec_id} – {kind} – '{term}': {err}")
                        continue
                    # answer = "DUMMY DELETEME"
                    output_records.append({
                        "record_id": rec_id,
                        "kind":      kind,
                        "term":      term,
                        "query":     prompt,
                        "abstract":  abstract,
                        "response":  answer,
                    })
                    processed_keys.add(key)
                    save_yaml(YAML_OUTPUT, output_records)
                    time.sleep(WAIT_TIME)

if __name__ == "__main__":
    main()
