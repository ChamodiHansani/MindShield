# baselines/eval_utils.py
import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

RESULTS_DIR = "results"

def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)

def evaluate_and_save(model_name, y_true, y_pred, class_names=None):
    ensure_results_dir()

    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro")
    f1_weighted = f1_score(y_true, y_pred, average="weighted")

    report = classification_report(
        y_true, y_pred,
        target_names=class_names if class_names else None,
        output_dict=True,
        zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred)

    # Save JSON report
    with open(os.path.join(RESULTS_DIR, f"{model_name}_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Save confusion matrix
    pd.DataFrame(cm).to_csv(os.path.join(RESULTS_DIR, f"{model_name}_confusion_matrix.csv"), index=False)

    # Append summary to results.csv
    summary_path = os.path.join(RESULTS_DIR, "baseline_summary.csv")
    row = pd.DataFrame([{
        "model": model_name,
        "accuracy": acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted
    }])

    if os.path.exists(summary_path):
        old = pd.read_csv(summary_path)
        new = pd.concat([old, row], ignore_index=True)
        new.to_csv(summary_path, index=False)
    else:
        row.to_csv(summary_path, index=False)

    return acc, f1_macro, f1_weighted
