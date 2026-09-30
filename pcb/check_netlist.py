"""Prove the schematic and the board describe the same circuit.

Exports the schematic netlist (kicad-cli) and compares every named net, pin by pin, with the pads on
opencycle.kicad_pcb. Single-pin 'unconnected-*' nets (no-connect pins) are ignored on both sides.

python check_netlist.py      -> prints 'netlist match' or the differences (exit 1)
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).parent


def sch_nets():
    env = dict(os.environ, KICAD7_SYMBOL_DIR="/usr/share/kicad/symbols")
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "-o", str(HERE / "opencycle.net"),
                    str(HERE / "opencycle.kicad_sch")], check=True, capture_output=True, env=env)
    txt = (HERE / "opencycle.net").read_text()
    nets = {}
    chunks = re.split(r'\n    \(net ', txt)[1:]
    for ch in chunks:
        m = re.match(r'\(code "?\d+"?\) \(name "([^"]*)"\)', ch)
        name = m.group(1).lstrip("/")
        nodes = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', ch))
        nodes = {(r, p) for r, p in nodes if not r.startswith("#")}
        if name.startswith("unconnected-") or not nodes:
            continue
        nets[name] = nodes
    return nets


def pcb_nets():
    sys.path.insert(0, str(HERE))
    import design as D
    from symlib import pins
    # footprints with mechanical "MP" tabs whose symbol has no MountPin (e.g. side switches): the tabs are
    # grounded on the board (build_pcb.py) but cannot appear in the schematic - skip them here
    no_mp = {p["ref"] for p in D.PARTS if p["pins"] and "MountPin" not in {n for _, n, *_ in pins(p["slib"], p["sym"])}}
    b = pcbnew.LoadBoard(str(HERE / "opencycle.kicad_pcb"))
    nets = {}
    for f in b.GetFootprints():
        ref = f.GetReference()
        if ref.startswith(("H", "FID")):
            continue
        for p in f.Pads():
            if p.GetNumber() and p.GetNetname():
                num = p.GetNumber()
                if num == "MP" and ref in no_mp:
                    continue
                nets.setdefault(p.GetNetname(), set()).add((ref, num))
    return nets


def main():
    s, p = sch_nets(), pcb_nets()
    problems = []
    for n in sorted(set(s) | set(p)):
        a, b = s.get(n, set()), p.get(n, set())
        # symbols with mounting pins map "MountPin" -> pad "MP"; the pad side lists MP once per pad
        a = {(r, "MP" if pin == "MountPin" else pin) for r, pin in a}
        if a != b:
            problems.append(f"{n}: only in schematic {sorted(a - b)}  only on board {sorted(b - a)}")
    if problems:
        print("\n".join(problems))
        return 1
    print(f"netlist match: {len(s)} nets, {sum(len(v) for v in s.values())} pin connections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
