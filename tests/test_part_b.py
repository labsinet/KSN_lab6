import re

import pytest

from tests.conftest import SUB, check, load
from tests.plan import MASK, PORTS, VLANS


def _vlan_defined(cfg, vlan):
    if cfg.has_block(rf"vlan {vlan}$"):
        return True
    p = SUB / "SW2_vlan.txt"
    if p.is_file():
        txt = p.read_text(encoding="utf-8", errors="replace")
        return re.search(rf"^\s*{vlan}\s+\S+\s+active", txt, re.M) is not None
    return False


@pytest.mark.points(0.5)
def test_b_router_physical_enabled():
    """Частина B: фізичний інтерфейс Gig0/0 на R2 ввімкнений"""
    cfg = load("R2.txt")
    itf = cfg.interfaces.get("gi0/0")
    check(itf, "На R2 немає інтерфейсу GigabitEthernet0/0.")
    check(not itf.shutdown, "GigabitEthernet0/0 вимкнений: виконайте 'no shutdown' на фізичному інтерфейсі.")


@pytest.mark.parametrize("vlan", VLANS)
@pytest.mark.points(0.5)
def test_b_router_subinterface(plan, vlan):
    """Частина B: підінтерфейс R2 для VLAN (dot1Q + IP шлюзу)"""
    cfg = load("R2.txt")
    subs = [i for n, i in cfg.interfaces.items() if n.startswith("gi0/0.")]
    check(subs, "На R2 немає підінтерфейсів GigabitEthernet0/0.X.")
    mine = [i for i in subs if i.encap_vlan == vlan]
    check(mine, f"Немає підінтерфейсу з 'encapsulation dot1Q {vlan}'.")
    gw = plan.vlan_gw[vlan]
    ok = [i for i in mine if (gw, MASK) in i.addrs()]
    check(ok, f"Підінтерфейс VLAN {vlan} має мати адресу {gw} {MASK}.")
    check(not ok[0].shutdown, f"Підінтерфейс {ok[0].raw_name} вимкнений.")


@pytest.mark.parametrize("vlan", VLANS)
@pytest.mark.points(0.5)
def test_b_switch_access_ports(vlan):
    """Частина B: VLAN створено, порти SW2 віднесено до VLAN"""
    cfg = load("SW2.txt")
    check(_vlan_defined(cfg, vlan),
          f"VLAN {vlan} не створено (немає 'vlan {vlan}' у конфігурації "
          "або запису в SW2_vlan.txt зі 'show vlan brief').")
    lo, hi = PORTS[vlan]
    for p in range(lo, hi + 1):
        itf = cfg.interfaces.get(f"fa0/{p}")
        check(itf, f"На SW2 немає інтерфейсу FastEthernet0/{p}.")
        check(itf.access_vlan == vlan,
              f"FastEthernet0/{p} має бути у VLAN {vlan} "
              f"('switchport access vlan {vlan}'), зараз: {itf.access_vlan}.")
        check(itf.mode != "trunk", f"FastEthernet0/{p} у режимі trunk, потрібен access.")


@pytest.mark.points(0.5)
def test_b_switch_trunk():
    """Частина B: порт SW2 до маршрутизатора (Gig0/1) у режимі trunk"""
    cfg = load("SW2.txt")
    itf = cfg.interfaces.get("gi0/1")
    check(itf, "На SW2 немає інтерфейсу GigabitEthernet0/1.")
    check(itf.mode == "trunk", "GigabitEthernet0/1 має бути 'switchport mode trunk'.")
    check(not itf.shutdown, "GigabitEthernet0/1 вимкнений.")
