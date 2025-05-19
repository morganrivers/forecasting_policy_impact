#!/usr/bin/env python3
"""
Evaluate outcome-grade forecasts (truth vs forecast YAMLs).
Adds scatter-plot and two baselines (mode + random).
"""
import yaml, math, collections, argparse, sys, random
from pathlib import Path
import matplotlib.pyplot as plt

GRADE_TO_SCORE = {
    "outcome was worsened":    0.00,
    "no effect":               0.25,
    "neutral/mixed results":   0.50,
    "significant":             0.75,
    "very significant":        1.00,
}
LABELS = list(GRADE_TO_SCORE)          # fixed order
VALID  = set(GRADE_TO_SCORE)

# ---------- helpers ----------------------------------------------------------

def load_yaml(path):
    if not Path(path).exists():
        sys.exit(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def rmse(y_true, y_pred):
    return math.sqrt(sum((p - t) ** 2 for p, t in zip(y_pred, y_true)) / len(y_true))

# ---------- main -------------------------------------------------------------

def main(truth, forecasts):
    truth_recs = load_yaml(truth)
    pred_recs  = load_yaml(forecasts)

    truth_map = {(r["record_id"], r["term"]): r["grade"].strip().lower()
                 for r in truth_recs}
    pred_map  = {(r["record_id"], r["term"]): r["grade"].strip().lower()
                 for r in pred_recs}

    y_true, y_pred = [], []
    for key, t_grade in truth_map.items():
        p_grade = pred_map.get(key)
        if t_grade in VALID and p_grade in VALID:
            y_true.append(GRADE_TO_SCORE[t_grade])
            y_pred.append(GRADE_TO_SCORE[p_grade])

    if not y_true:
        sys.exit("No overlapping records with valid grades.")

    # ── metrics ───────────────────────────────────────────────────────────────
    main_rmse = rmse(y_true, y_pred)
    main_acc  = sum(p == t for p, t in zip(y_pred, y_true)) / len(y_true)

    # macro-F1 (5-class)
    conf = collections.Counter((pred_map.get(k), v)
                               for k, v in truth_map.items() if v in VALID)
    f1s = []
    for g in VALID:
        tp = conf[(g, g)]
        fp = sum(conf[(g, x)] for x in VALID if x != g)
        fn = sum(conf[(x, g)] for x in VALID if x != g)
        prec = tp / (tp + fp) if tp + fp else 0
        rec  = tp / (tp + fn) if tp + fn else 0
        f1s.append(0 if prec + rec == 0 else 2*prec*rec/(prec+rec))
    macro_f1 = sum(f1s) / len(f1s)

    # ── baseline 1: most-common grade ─────────────────────────────────────────
    mode_grade, _ = collections.Counter(truth_map.values()).most_common(1)[0]
    mode_score    = GRADE_TO_SCORE[mode_grade]
    mode_rmse     = rmse(y_true, [mode_score]*len(y_true))
    mode_acc      = sum(t == mode_score for t in y_true) / len(y_true)

    # ── baseline 2: random grade ──────────────────────────────────────────────
    random_scores = [GRADE_TO_SCORE[random.choice(LABELS)] for _ in y_true]
    rand_rmse     = rmse(y_true, random_scores)
    rand_acc      = sum(r == t for r, t in zip(random_scores, y_true)) / len(y_true)

    # ── metrics ───────────────────────────────────────────────────────────────
    # Brier Score calculation
    y_true_binary = [1 if t >= 0.75 else 0 for t in y_true]
    brier_score = sum((f - t)**2 for f, t in zip(y_pred, y_true_binary)) / len(y_true_binary)

    # ── report ────────────────────────────────────────────────────────────────
    print("=== Forecast Evaluation ===")
    print(f"N overlap              : {len(y_true)}")
    print(f"RMSE                   : {main_rmse:.4f}")
    print(f"Accuracy (% correct)   : {main_acc:.3%}")
    print(f"Macro-F1               : {macro_f1:.4f}")
    print(f"Brier score (rough)    : {brier_score:.4f}")
    print("--- Baseline: most common grade")
    print(f"Grade                  : {mode_grade}")
    print(f"RMSE                   : {mode_rmse:.4f}")
    print(f"Accuracy               : {mode_acc:.3%}")
    print("--- Baseline: random grade")
    print(f"RMSE                   : {rand_rmse:.4f}")
    print(f"Accuracy               : {rand_acc:.3%}")

    # Brier score for the "most common grade" baseline
    mode_brier_score = sum((mode_score - t)**2 for t in y_true_binary) / len(y_true_binary)

    # Brier score for the "random grade" baseline
    rand_brier_score = sum((r - t)**2 for r, t in zip(random_scores, y_true_binary)) / len(y_true_binary)

    print("--- Baseline Brier Scores ---")
    print(f"Brier (most common)    : {mode_brier_score:.4f}")
    print(f"Brier (random)         : {rand_brier_score:.4f}")

    # ── histogram ─────────────────────────────────────────────────────────────
    truth_cnt = collections.Counter(truth_map.values())
    pred_cnt  = collections.Counter(pred_map.values())
    x = range(len(LABELS))
    plt.figure(figsize=(8,4))
    plt.bar(x,                   [truth_cnt[l] for l in LABELS],
            width=0.4, label="Truth", align="edge")
    plt.bar([i+0.4 for i in x],  [pred_cnt[l]  for l in LABELS],
            width=0.4, label="Forecast")
    plt.xticks([i+0.2 for i in x], LABELS, rotation=45, ha="right")
    plt.ylabel("Count"); plt.title("Grade distribution"); plt.legend()
    plt.tight_layout()

    # ── scatter ──────────────────────────────────────────────────────────────
    # plt.figure(figsize=(5,5))
    # plt.scatter(y_true, y_pred, alpha=0.6)
    # plt.plot([0,1], [0,1], linestyle="--", linewidth=1)
    # plt.xlabel("True score"); plt.ylabel("Forecast score")
    # plt.title("Scatter: True vs Forecast numeric scores")
    # plt.tight_layout()
    # plt.show()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Evaluate grade forecasts")
    p.add_argument("--truth", default="abstract_outcome_grades.yaml")
    p.add_argument("--forecasts", default="abstract_outcome_forecasts.yaml")
    args = p.parse_args()
    main(args.truth, args.forecasts)