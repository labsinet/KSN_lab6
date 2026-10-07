"""Генератор еталонних конфігурацій (Packet Tracer-стиль) для самоперевірки тестів."""
from tests.plan import Plan, MASK, PORTS


def _hdr(host):
    return f"Building configuration...\n\nCurrent configuration : 900 bytes\n!\nversion 15.1\nhostname {host}\n!\n"


def r1(n, lan1_wrong=False, shut2=False):
    p = Plan(n)
    ip1 = p.gw1 if not lan1_wrong else p.gw1.replace(".254", ".1")
    return (_hdr("R1") +
            f"interface GigabitEthernet0/0\n ip address {ip1} {MASK}\n duplex auto\n speed auto\n!\n"
            f"interface GigabitEthernet0/1\n ip address {p.gw2} {MASK}\n duplex auto\n speed auto\n"
            f"{' shutdown' + chr(10) if shut2 else ''}!\n"
            "interface Vlan1\n no ip address\n shutdown\n!\nend\n")


def r2(n, drop_vlan=None, phys_shut=False):
    p = Plan(n)
    s = _hdr("R2") + "interface GigabitEthernet0/0\n no ip address\n duplex auto\n speed auto\n"
    s += (" shutdown\n" if phys_shut else "") + "!\n"
    for v in (10, 20, 30):
        if v == drop_vlan:
            continue
        s += (f"interface GigabitEthernet0/0.{v}\n encapsulation dot1Q {v}\n"
              f" ip address {p.vlan_gw[v]} {MASK}\n!\n")
    return s + "interface GigabitEthernet0/1\n no ip address\n shutdown\n!\nend\n"


def sw2(trunk=True, wrong_port=False):
    s = _hdr("SW2")
    for v, (lo, hi) in PORTS.items():
        for port in range(lo, hi + 1):
            vv = 20 if (wrong_port and port == 1) else v
            s += (f"interface FastEthernet0/{port}\n switchport access vlan {vv}\n"
                  " switchport mode access\n!\n")
    s += "interface GigabitEthernet0/1\n" + (" switchport mode trunk\n" if trunk else "") + "!\nend\n"
    return s


VLAN_BRIEF = """VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/7, Fa0/8
10   Designers                        active    Fa0/1, Fa0/2
20   Accounting                       active    Fa0/3, Fa0/4
30   Admin                            active    Fa0/5, Fa0/6
"""


def write_submission(d, n, **kw):
    d.mkdir(parents=True, exist_ok=True)
    (d / "variant.txt").write_text(f"{n}\n")
    (d / "R1.txt").write_text(r1(n, **kw.get("r1", {})))
    (d / "R2.txt").write_text(r2(n, **kw.get("r2", {})))
    (d / "SW2.txt").write_text(sw2(**kw.get("sw2", {})))
    (d / "SW2_vlan.txt").write_text(VLAN_BRIEF)
    (d / "project.pkt").write_bytes(b"PKT")
