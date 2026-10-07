import pytest

from tests.conftest import check, load
from tests.plan import MASK


def _find(cfg, ip, lan):
    itf = cfg.find_iface_with_ip(ip, MASK)
    check(itf, f"Не знайдено інтерфейс з адресою {ip} {MASK} (шлюз {lan}/24). "
               "Перевірте адресу, маску та номер варіанта.")
    return itf


@pytest.mark.points(1)
def test_a_lan1_gateway(plan):
    """Частина A: інтерфейс R1 у LAN-1 має адресу шлюзу .254/24"""
    _find(load("R1.txt"), plan.gw1, plan.lan1)


@pytest.mark.points(1)
def test_a_lan2_gateway(plan):
    """Частина A: інтерфейс R1 у LAN-2 має адресу шлюзу .254/24"""
    _find(load("R1.txt"), plan.gw2, plan.lan2)


@pytest.mark.points(1)
def test_a_interfaces_enabled(plan):
    """Частина A: обидва інтерфейси різні та ввімкнені (no shutdown)"""
    cfg = load("R1.txt")
    i1 = _find(cfg, plan.gw1, plan.lan1)
    i2 = _find(cfg, plan.gw2, plan.lan2)
    check(i1.name != i2.name,
          "Обидві адреси призначено на один інтерфейс; потрібні два різні (Gig0/0 і Gig0/1).")
    for i in (i1, i2):
        check(not i.shutdown, f"Інтерфейс {i.raw_name} вимкнений: додайте 'no shutdown'.")
