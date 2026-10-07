"""Адресація за номером варіанта (1-18). Дивись розділ 2 методички."""
MASK = "255.255.255.0"
VLANS = (10, 20, 30)
VLAN_NAMES = {10: "Дизайн", 20: "Бухгалтерія", 30: "Адміністрація"}
PORTS = {10: (1, 2), 20: (3, 4), 30: (5, 6)}  # FastEthernet0/x на SW2


class Plan:
    def __init__(self, n: int):
        self.n = n
        x = n if n <= 9 else n + 1
        self.lan1 = f"192.168.{x}.0"
        self.lan2 = f"192.168.{n * 10}.0"
        self.gw1 = f"192.168.{x}.254"
        self.gw2 = f"192.168.{n * 10}.254"
        self.vlan_net = {v: f"10.{n}.{v}.0" for v in VLANS}
        self.vlan_gw = {v: f"10.{n}.{v}.254" for v in VLANS}
