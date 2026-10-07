"""Формує звіт автоперевірки у GitHub Step Summary та анотації помилок."""
import json
import os
import sys
from pathlib import Path

p = Path(os.environ.get("GRADE_FILE", "grade.json"))
if not p.exists():
    print("::error::grade.json не створено — тести не запустилися.")
    sys.exit(0)
g = json.loads(p.read_text(encoding="utf-8"))
lines = [f"## Автоперевірка практичної №6",
         f"**Варіант:** {g['variant'] or '—'}   **Оцінка (авто):** "
         f"**{g['score']:g} / {g['max']:g}**",
         "", "| Перевірка | Бали | Результат | Підказка |", "|---|:-:|:-:|---|"]
for t in g["tests"]:
    got = t["points"] if t["passed"] else 0
    lines.append(f"| {t['title']} | {got:g}/{t['points']:g} | "
                 f"{'✅' if t['passed'] else '❌'} | {t['message'].replace('|', '/')} |")
    if not t["passed"]:
        print(f"::error title={t['title']}::{t['message']}")
lines += ["", "_Автоматична частина (8 балів). Звіт і відповіді (2 бали) оцінює викладач._"]
out = "\n".join(lines)
print(out)
summ = os.environ.get("GITHUB_STEP_SUMMARY")
if summ:
    with open(summ, "a", encoding="utf-8") as f:
        f.write(out + "\n")
