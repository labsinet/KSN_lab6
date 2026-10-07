"""Перегенерація integrity.sha256 після змін у тестах: python teacher/make_checksum.py"""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent.parent
files = sorted([*root.glob("tests/*.py"), root / "pytest.ini",
                root / ".github/scripts/summary.py", root / ".github/workflows/autograde.yml"])
(root / "integrity.sha256").write_text("".join(
    f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(root).as_posix()}\n"
    for f in files))
print("integrity.sha256 оновлено")
