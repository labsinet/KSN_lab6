import pytest

from tests.conftest import SUB, check

REQUIRED = ["R1.txt", "R2.txt", "SW2.txt"]


@pytest.mark.points(0.25)
def test_variant_valid(variant):
    """Формат: variant.txt містить коректний номер варіанта (1-18)"""
    check(1 <= variant <= 18, "Некоректний номер варіанта.")


@pytest.mark.points(0.5)
def test_config_files_present():
    """Формат: подано R1.txt, R2.txt, SW2.txt з вмістом конфігурації"""
    for name in REQUIRED:
        p = SUB / name
        check(p.is_file(), f"Не знайдено submission/{name}.")
        txt = p.read_text(encoding="utf-8", errors="replace").lower()
        check("interface" in txt,
              f"{name}: немає рядків 'interface ...'. Вставте вивід 'show startup-config'.")


@pytest.mark.points(0.25)
def test_pkt_present():
    """Формат: додано файл проєкту Packet Tracer (.pkt)"""
    check(any(SUB.glob("*.pkt")), "У submission/ немає жодного файлу .pkt.")
