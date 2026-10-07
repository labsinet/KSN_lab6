"""Самоперевірка автотестів: еталони мають давати максимум, помилки — втрату балів."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from teacher.fixtures import write_submission

ROOT = Path(__file__).resolve().parent.parent


def grade(sub: Path):
    env = dict(os.environ, SUBMISSION_DIR=str(sub), GRADE_FILE=str(sub / "grade.json"))
    subprocess.run([sys.executable, "-m", "pytest", "tests", "-p", "no:cacheprovider"],
                   cwd=ROOT, env=env, capture_output=True)
    return json.loads((sub / "grade.json").read_text(encoding="utf-8"))


def failed(g):
    return {t["title"] for t in g["tests"] if not t["passed"]}


@pytest.mark.parametrize("n", [1, 3, 9, 10, 18])
def test_reference_gets_full_score(tmp_path, n):
    write_submission(tmp_path, n)
    g = grade(tmp_path)
    assert g["score"] == g["max"] == 8.0, failed(g)


def test_wrong_variant_addresses_lose_points(tmp_path):
    write_submission(tmp_path, 3)
    (tmp_path / "variant.txt").write_text("4\n")
    g = grade(tmp_path)
    assert g["score"] < g["max"]
    assert any("LAN-1" in t for t in failed(g))


@pytest.mark.parametrize("kw,needle", [
    ({"r1": {"lan1_wrong": True}}, "LAN-1"),
    ({"r1": {"shut2": True}}, "ввімкнені"),
    ({"r2": {"drop_vlan": 20}}, "підінтерфейс"),
    ({"r2": {"phys_shut": True}}, "Gig0/0"),
    ({"sw2": {"trunk": False}}, "trunk"),
    ({"sw2": {"wrong_port": True}}, "порти SW2"),
])
def test_single_mistake_detected(tmp_path, kw, needle):
    write_submission(tmp_path, 5, **kw)
    g = grade(tmp_path)
    assert g["score"] < g["max"]
    assert any(needle in t for t in failed(g)), failed(g)


def test_template_placeholders_score_zero_without_crash():
    g = grade(ROOT / "submission")
    assert g["score"] == 0
    assert g["max"] == 8.0


def test_not_saved_config_detected(tmp_path):
    write_submission(tmp_path, 2)
    (tmp_path / "R1.txt").write_text("interface x\n startup-config is not present\n")
    g = grade(tmp_path)
    assert any("LAN-1" in t for t in failed(g))
