import json
import os
import urllib.request
import datetime as dt
from collections import Counter

HANDLE = "cloudielst"
OUT = "assets/cf-heatmap.svg"
CELL, GAP = 11, 3
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def level(n):
    if n == 0:
        return 0
    if n <= 2:
        return 1
    if n <= 4:
        return 2
    if n <= 8:
        return 3
    return 4


url = f"https://codeforces.com/api/user.status?handle={HANDLE}"
with urllib.request.urlopen(url, timeout=30) as r:
    subs = json.load(r)["result"]

counts = Counter(
    dt.datetime.fromtimestamp(s["creationTimeSeconds"], dt.timezone.utc).date()
    for s in subs
)

today = dt.datetime.now(dt.timezone.utc).date()
start = today - dt.timedelta(days=364)
start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # align to Sunday

cells = []
d = start
while d <= today:
    week = (d - start).days // 7
    dow = (d.weekday() + 1) % 7
    n = counts.get(d, 0)
    x = week * (CELL + GAP)
    y = 24 + dow * (CELL + GAP)
    cells.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
        f'fill="{COLORS[level(n)]}"><title>{d}: {n} submissions</title></rect>'
    )
    d += dt.timedelta(days=1)

weeks = (today - start).days // 7 + 1
width = weeks * (CELL + GAP)
height = 24 + 7 * (CELL + GAP)
total = sum(v for k, v in counts.items() if k >= start)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}">'
    f'<text x="0" y="12" fill="#8b949e" font-family="sans-serif" font-size="12">'
    f"{total} Codeforces submissions in the last year ({HANDLE})</text>"
    + "".join(cells)
    + "</svg>"
)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Wrote {OUT}: {total} submissions")
