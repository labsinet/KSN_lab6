"""Простий парсер текстових конфігурацій Cisco IOS (running/startup-config)."""
import re

CLEAN_RE = re.compile(r"--More--|\x08+|\x1b\[[0-9;]*[A-Za-z]")


def norm_if(name: str) -> str:
    """'GigabitEthernet0/0.10' / 'gig 0/0.10' / 'g0/0.10' -> 'gi0/0.10'."""
    s = re.sub(r"\s+", "", name.lower())
    m = re.match(r"(gigabitethernet|gig|gi|g)(\d.*)$", s)
    if m:
        return "gi" + m.group(2)
    m = re.match(r"(fastethernet|fas|fa|f)(\d.*)$", s)
    if m:
        return "fa" + m.group(2)
    return s


class Interface:
    def __init__(self, header: str, lines: list):
        m = re.match(r"interface\s+(\S.*)", header, re.I)
        self.raw_name = m.group(1).strip()
        self.name = norm_if(self.raw_name)
        self.lines = [l.strip() for l in lines]

    def _m(self, pattern):
        for l in self.lines:
            m = re.match(pattern, l, re.I)
            if m:
                return m
        return None

    def addrs(self):
        out = []
        for l in self.lines:
            m = re.match(r"ip address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)", l, re.I)
            if m:
                out.append((m.group(1), m.group(2)))
        return out

    @property
    def shutdown(self) -> bool:
        return any(l.lower() == "shutdown" for l in self.lines)

    @property
    def encap_vlan(self):
        m = self._m(r"encapsulation dot1q (\d+)")
        return int(m.group(1)) if m else None

    @property
    def access_vlan(self):
        m = self._m(r"switchport access vlan (\d+)")
        return int(m.group(1)) if m else None

    @property
    def mode(self):
        m = self._m(r"switchport mode (\w+)")
        return m.group(1).lower() if m else None


class Config:
    def __init__(self, text: str):
        self.text = CLEAN_RE.sub("", text)
        self.blocks = []  # (header, [children])
        cur = None
        for raw in self.text.splitlines():
            line = raw.rstrip()
            if not line.strip():
                continue
            if line.lstrip().startswith("!"):
                cur = None
                continue
            if line[0] in " \t" and cur is not None:
                cur[1].append(line)
            else:
                cur = (line.strip(), [])
                self.blocks.append(cur)
        self.interfaces = {}
        for header, lines in self.blocks:
            if re.match(r"interface\s+\S", header, re.I) and not re.match(
                    r"interface\s+range", header, re.I):
                itf = Interface(header, lines)
                self.interfaces[itf.name] = itf

    @property
    def not_saved(self) -> bool:
        return "startup-config is not present" in self.text.lower()

    def has_block(self, pattern) -> bool:
        return any(re.match(pattern, h, re.I) for h, _ in self.blocks)

    def find_iface_with_ip(self, ip, mask):
        for itf in self.interfaces.values():
            if (ip, mask) in itf.addrs():
                return itf
        return None
