import subprocess
import sys

SCRIPTS = [
    "baselines.train_logreg",
    "baselines.train_svm",
    "baselines.train_nb",
    "baselines.train_rf",
    "baselines.train_knn",
    "baselines.train_dt",
]

def main():
    print("run_all started ✅", flush=True)
    for mod in SCRIPTS:
        print(f"\n=== Running: {mod} ===", flush=True)
        subprocess.check_call([sys.executable, "-m", mod])

    print("\nDone ✅ Check results/baseline_summary.csv", flush=True)

if __name__ == "__main__":
    main()
