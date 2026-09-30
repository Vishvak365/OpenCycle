"""Route the board with Freerouting (Specctra DSN/SES round trip).

python autoroute.py placed.kicad_pcb routed.kicad_pcb [passes]

- adds the inner planes (In1 GND, In2 +3V3) so Freerouting treats them as planes and only fans out to them
- writes net classes into the DSN (power nets wider, default 0.2 mm / 0.15 mm clearance)
- runs Freerouting headless (xvfb) and imports the session back into KiCad
Freerouting 1.9.0 jar: downloaded to pcb/freerouting-1.9.0.jar on first run (git-ignored).
"""
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design as D  # noqa: E402
from finish import add_zone  # noqa: E402
from ses_import import import_ses  # noqa: E402

HERE = Path(__file__).parent
JAR = HERE / "freerouting-1.9.0.jar"
JAR_URL = "https://github.com/freerouting/freerouting/releases/download/v1.9.0/freerouting-1.9.0.jar"


def um(mm):
    return int(round(mm * 1000))


def add_classes(dsn_text):
    """Move the power/RF nets out of KiCad's default class into width classes (DSN units are um)."""
    m = re.search(r"\(class kicad_default(.*?)\n    \)\n", dsn_text, flags=re.S)
    block = m.group(0)
    head, rest = block.split("(circuit", 1)
    raw = re.findall(r'"[^"]*"|[^\s()]+', head.replace("(class kicad_default", ""))
    names = [n.strip('"') for n in raw]
    groups = {}
    for n, w in D.POWER_NETS.items():
        if n in names and n not in D.PLANE_NETS:
            groups.setdefault(w, []).append(n)
    moved = {n for ns in groups.values() for n in ns}
    keep = [r for r, n in zip(raw, names) if n not in moved]
    via = re.search(r"\(use_via ([^)]+)\)", rest).group(1)
    new = "    (class kicad_default " + " ".join(keep) + "\n      (circuit" + rest
    for w, ns in sorted(groups.items()):
        new += (f"    (class W{um(w)} " + " ".join(f'"{n}"' if not re.match(r"^[A-Za-z0-9_]+$", n) else n for n in ns)
                + f"\n      (circuit\n        (use_via {via})\n      )\n"
                + f"      (rule\n        (width {um(w)})\n        (clearance {um(0.15)})\n      )\n    )\n")
    return dsn_text.replace(block, new)


def main(src, dst, passes=40):
    b = pcbnew.LoadBoard(src)
    add_zone(b, "GND", pcbnew.In1_Cu, 0)
    add_zone(b, "+3V3", pcbnew.In2_Cu, 0)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    tmp = HERE / "work.kicad_pcb"
    b.Save(str(tmp))
    dsn = HERE / "work.dsn"
    ses = HERE / "work.ses"
    ok = pcbnew.ExportSpecctraDSN(b, str(dsn))
    if not ok:
        raise SystemExit("DSN export failed")
    dsn.write_text(add_classes(dsn.read_text()))
    if not JAR.exists():
        urllib.request.urlretrieve(JAR_URL, JAR)
    if ses.exists():
        ses.unlink()
    cmd = ["xvfb-run", "-a", "java", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses), "-mp", str(passes),
           "-mt", "1", "-da"]
    print(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    (HERE / "freerouting.log").write_text(r.stdout + r.stderr)
    if not ses.exists():
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit("Freerouting produced no session file")
    b2 = pcbnew.LoadBoard(str(tmp))
    print("imported tracks/vias:", import_ses(b2, str(ses)))
    b2.Save(dst)
    print("routed ->", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 40)
