import csv
import os
import sys

CSV_PATH = os.getenv("LOCUST_CSV_PREFIX", "locust_stats") + "_stats.csv"

MAX_FAIL_RATIO = float(os.getenv("MAX_FAIL_RATIO", "0.01"))  # 1%
MAX_P95_MS = int(os.getenv("MAX_P95_MS", "500"))  # 500ms

def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: Missing Locust stats file: {CSV_PATH}")
        sys.exit(1)

    total_reqs = 0
    total_fails = 0
    worst_p95 = 0

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                total_reqs = int(row["# requests"])
                total_fails = int(row["# failures"])
                worst_p95 = int(float(row["95%"]))
                break

    if total_reqs == 0:
        print("ERROR: No requests executed.")
        sys.exit(1)

    fail_ratio = total_fails / total_reqs
    print(f"Requests: {total_reqs}, Failures: {total_fails}, Fail ratio: {fail_ratio:.4f}, P95: {worst_p95} ms")

    if fail_ratio > MAX_FAIL_RATIO:
        print(f"FAIL: fail_ratio {fail_ratio:.4f} > {MAX_FAIL_RATIO}")
        sys.exit(1)

    if worst_p95 > MAX_P95_MS:
        print(f"FAIL: p95 {worst_p95}ms > {MAX_P95_MS}ms")
        sys.exit(1)

    print("PASS: thresholds OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
