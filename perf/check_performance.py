import csv
import os
import sys

CSV_PATH = os.getenv("LOCUST_CSV_PREFIX", "locust_stats") + "_stats.csv"

MAX_FAIL_RATIO = float(os.getenv("MAX_FAIL_RATIO", "0.01"))  # 1%
MAX_P95_MS = int(os.getenv("MAX_P95_MS", "500"))  # 500ms


def _first_existing(row: dict, keys: list[str], default=None):
    """Return first existing key from keys in row."""
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return default


def _to_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


def _find_aggregated_row(rows: list[dict]) -> dict | None:
    """
    Locust versions differ:
    - some use Name == "Aggregated"
    - some use Type == "Aggregated"
    - some have only a blank Type and Name == "Aggregated"
    """
    for r in rows:
        name = (r.get("Name") or "").strip()
        typ = (r.get("Type") or "").strip()
        if name.lower() == "aggregated" or typ.lower() == "aggregated":
            return r
    return None


def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: Missing Locust stats file: {CSV_PATH}")
        sys.exit(1)

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("ERROR: Locust stats file is empty.")
        sys.exit(1)

    agg = _find_aggregated_row(rows)
    if not agg:
        # fallback: sometimes last row is aggregated-ish, but let's be explicit
        print("ERROR: Could not find 'Aggregated' row in Locust CSV.")
        print(f"DEBUG: CSV columns: {list(rows[0].keys())}")
        sys.exit(1)

    # Column name differences across Locust versions
    reqs_val = _first_existing(
        agg,
        ["# requests", "# reqs", "Request Count", "Requests", "Total Requests"],
        default="0",
    )
    fails_val = _first_existing(
        agg,
        ["# failures", "# fails", "Failure Count", "Failures", "Total Failures"],
        default="0",
    )
    p95_val = _first_existing(
        agg,
        ["95%", "95%ile", "P95", "p95", "95th percentile"],
        default="0",
    )

    total_reqs = _to_int(reqs_val, 0)
    total_fails = _to_int(fails_val, 0)
    worst_p95 = _to_int(p95_val, 0)

    if total_reqs == 0:
        print("ERROR: No requests executed (total_reqs == 0).")
        print(f"DEBUG: Aggregated row: {agg}")
        sys.exit(1)

    fail_ratio = total_fails / total_reqs
    print(
        f"Requests: {total_reqs}, Failures: {total_fails}, "
        f"Fail ratio: {fail_ratio:.4f}, P95: {worst_p95} ms"
    )

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
