import csv, os, statistics, time
from collections import defaultdict
from datetime import datetime

DELAY = float(os.getenv("DELAY", "0"))

rows = list(csv.DictReader(open("transactions.csv")))
by_cust = defaultdict(list)
for r in rows:
    r["amount"] = float(r["amount"])
    r["time"] = datetime.strptime(r["time"], "%Y-%m-%d %H:%M")
    by_cust[r["customer"]].append(r)

flagged = []
done = 0
for cust, txns in by_cust.items():
    txns.sort(key=lambda t: t["time"])
    median = statistics.median(t["amount"] for t in txns)
    for i, t in enumerate(txns):
        done += 1
        print(f"Scanning {done}/{len(rows)}: {t['txn_id']}", flush=True)
        time.sleep(DELAY)
        if t["amount"] > 5 * median:
            flagged.append([t["txn_id"], cust, t["amount"], t["town"],
                            f"Amount > 5x customer median ({median:,.0f})"])
        if i > 0:
            p = txns[i - 1]
            mins = (t["time"] - p["time"]).total_seconds() / 60
            if p["town"] != t["town"] and mins <= 10:
                flagged.append([t["txn_id"], cust, t["amount"], t["town"],
                                f"{p['town']} to {t['town']} in {mins:.0f} min"])

with open("flagged_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["txn_id", "customer", "amount", "town", "reason"])
    w.writerows(flagged)

print("\n=== FLAGGED TRANSACTIONS ===")
for row in flagged:
    print(row)
print(f"\n{len(flagged)} suspicious transactions saved to flagged_results.csv")
print("Idle capacity helps protect customers from fraud.")
