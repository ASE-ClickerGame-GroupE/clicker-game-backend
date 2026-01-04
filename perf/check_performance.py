import csv
import sys

MAX_P95_MS = 400
MAX_FAILURE_RATE = 0.05

with open("locust_stats_stats.csv", newline="") as f:
    reader = csv.DictReader(f)
    row = next(r for r in reader if r["Name"] == "Aggregated")

total_requests = int(row["Request Count"])
total_failures = int(row["Failure Count"])
p95 = float(row["95%"])

failure_rate = (total_failures / total_requests) if total_requests else 0

print(p95)
print(failure_rate)

if p95 > MAX_P95_MS:
    sys.exit(1)

if failure_rate > MAX_FAILURE_RATE:
    sys.exit(1)

sys.exit(0)

