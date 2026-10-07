import json
import os
import re
from pathlib import Path

import pytest

from tests.ciscoparse import Config
from tests.plan import Plan

SUB = Path(os.environ.get("SUBMISSION_DIR", "submission"))
GRADE_FILE = Path(os.environ.get("GRADE_FILE", "grade.json"))
RESULTS = []
STATE = {"variant": None}


def check(cond, msg):
    if not cond:
        pytest.fail(msg, pytrace=False)


def read_file(name):
    p = SUB / name
    check(p.is_file(), f"Файл {SUB.name}/{name} не знайдено.")
    txt = p.read_text(encoding="utf-8", errors="replace")
    check(txt.strip() and "interface" in txt.lower() or name.endswith("vlan.txt"),
          f"Файл {name} порожній або не схожий на конфігурацію Cisco "
          "(немає рядків 'interface ...').")
    return txt


def load(name) -> Config:
    cfg = Config(read_file(name))
    check(not cfg.not_saved,
          f"{name}: конфігурацію не збережено (startup-config is not present). "
          "Виконайте 'copy running-config startup-config'.")
    return cfg


@pytest.fixture(scope="session")
def variant():
    p = SUB / "variant.txt"
    check(p.is_file(), "Файл submission/variant.txt не знайдено.")
    txt = p.read_text(encoding="utf-8", errors="replace").strip()
    check(re.fullmatch(r"\d{1,2}", txt) and 1 <= int(txt) <= 18,
          f"variant.txt має містити одне число від 1 до 18, а там: '{txt[:30]}'.")
    STATE["variant"] = int(txt)
    return int(txt)


@pytest.fixture(scope="session")
def plan(variant):
    return Plan(variant)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" or (rep.when == "setup" and not rep.passed):
        m = item.get_closest_marker("points")
        doc = (item.function.__doc__ or item.name).strip().splitlines()[0]
        param = item.name[item.name.find("["):] if "[" in item.name else ""
        msg = ""
        if call.excinfo is not None:
            msg = str(call.excinfo.value).strip().splitlines()[0] if str(
                call.excinfo.value).strip() else repr(call.excinfo.value)
        RESULTS.append({
            "id": item.nodeid, "title": f"{doc} {param}".strip(),
            "points": float(m.args[0]) if m else 0.0,
            "passed": rep.passed, "message": msg,
        })


def pytest_sessionfinish(session, exitstatus):
    score = sum(r["points"] for r in RESULTS if r["passed"])
    total = sum(r["points"] for r in RESULTS)
    GRADE_FILE.write_text(json.dumps(
        {"variant": STATE["variant"], "score": round(score, 2),
         "max": round(total, 2), "tests": RESULTS}, ensure_ascii=False, indent=2),
        encoding="utf-8")


def pytest_terminal_summary(terminalreporter):
    score = sum(r["points"] for r in RESULTS if r["passed"])
    total = sum(r["points"] for r in RESULTS)
    terminalreporter.write_line(f"\nАвтоматична оцінка: {score:g} / {total:g}")
