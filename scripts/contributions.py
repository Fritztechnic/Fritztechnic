"""Render the GitHub contribution heatmap as a themed SVG (levels from ghchart.rshah.org)."""
import re, sys, urllib.request
from datetime import date, timedelta

USER = sys.argv[1] if len(sys.argv) > 1 else "Fritztechnic"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/contributions.svg"
FONT = "'Noto Sans', 'Segoe UI', 'Open Sans', -apple-system, Helvetica, Arial, sans-serif"
LEVELS = ["#151b23", "#0e4429", "#006d32", "#26a641", "#39d353"]

req = urllib.request.Request(f"https://ghchart.rshah.org/{USER}", headers={"User-Agent": "curl/8"})
src = urllib.request.urlopen(req, timeout=30).read().decode()
days = {date.fromisoformat(d): int(s) for s, d in re.findall(r'data-score="(\d+)" data-date="([\d-]+)"', src)}
start = min(days)
start -= timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday

def level(n):  # ghchart already reports activity levels 0-4
    return min(4, n)

S, G, X0, Y0, P = 11, 3, 86, 84, 28
W = 830
cells, months, last = [], [], None
for d, n in sorted(days.items()):
    col, row = (d - start).days // 7, (d.weekday() + 1) % 7
    x, y = X0 + col * (S + G), Y0 + row * (S + G)
    cells.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" fill="{LEVELS[level(n)]}"/>')
    if d.day <= 7 and row == 0 and d.month != last:
        last = d.month
        months.append(f'<text x="{x}" y="{Y0 - 10}" font-size="11" fill="#8b949e">{d.strftime("%b")}</text>')
H = Y0 + 7 * (S + G) + 50
rows = "".join(f'<text x="{P}" y="{Y0 + r * (S + G) + 10}" font-size="11" fill="#8b949e">{t}</text>'
                for r, t in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
lx = W - P - 5 * (S + G) - 90
legend = (f'<text x="{lx}" y="{H - 22}" font-size="11" fill="#8b949e">Less</text>'
          + "".join(f'<rect x="{lx + 36 + i * (S + G)}" y="{H - 31}" width="{S}" height="{S}" fill="{c}"/>' for i, c in enumerate(LEVELS))
          + f'<text x="{lx + 36 + 5 * (S + G) + 4}" y="{H - 22}" font-size="11" fill="#8b949e">More</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="#0d0f13" stroke="#2a2f38"/>
<rect x="{P}" y="0" width="48" height="2" fill="#d10606"/>
<text x="{P}" y="{P+10}" font-size="11" letter-spacing="2" font-weight="600" fill="#8b949e">CONTRIBUTIONS / LAST YEAR</text>
<line x1="{P}" y1="{P+24}" x2="{W-P}" y2="{P+24}" stroke="#2a2f38"/>
{"".join(months)}{rows}
{"".join(cells)}
{legend}
</svg>
'''
open(OUT, "w").write(svg)
