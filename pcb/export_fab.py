"""Write everything needed to order and assemble the board into pcb/fab/.

python export_fab.py

fab/gerbers/*              Gerber X2 + Excellon drill (+ map), zipped as fab/opencycle_v0.2_gerbers.zip (upload to JLCPCB)
fab/bom_jlcpcb.csv         JLCPCB assembly BOM (Comment, Designator, Footprint, Manufacturer, MPN)
fab/cpl_jlcpcb.csv         JLCPCB pick-and-place (Designator, Mid X, Mid Y, Layer, Rotation)
fab/bom_distributors.csv   Mouser / Digi-Key order list with part numbers, qty, price, links
fab/assembly_front.pdf     assembly drawings (fab layer with reference designators)
fab/assembly_back.pdf
fab/opencycle_schematic.pdf (from gen_schematic.py)
"""
import csv
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import design as D  # noqa: E402
import sourcing as SRC  # noqa: E402

BOARD = HERE / "opencycle.kicad_pcb"
FAB = HERE / "fab"
ENV = dict(os.environ, KICAD7_FOOTPRINT_DIR="/usr/share/kicad/footprints", KICAD7_SYMBOL_DIR="/usr/share/kicad/symbols")
ENV.pop("LD_LIBRARY_PATH", None)
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"


def run(*args):
    r = subprocess.run(["kicad-cli", *args], capture_output=True, text=True, env=ENV)
    if r.returncode != 0:
        raise SystemExit(f"kicad-cli {' '.join(args)} failed:\n{r.stdout}\n{r.stderr}")


def gerbers():
    g = FAB / "gerbers"
    shutil.rmtree(g, ignore_errors=True)
    g.mkdir(parents=True)
    run("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "-o", str(g) + "/", str(BOARD))
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map",
        "--map-format", "pdf", "-o", str(g) + "/", str(BOARD))
    z = FAB / "opencycle_v0.2_gerbers.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(g.iterdir()):
            zf.write(f, f.name)
    return sorted(p.name for p in g.iterdir())


def assembly_pdfs():
    run("pcb", "export", "pdf", "--layers", "F.Fab,Edge.Cuts,F.Silkscreen", "--include-border-title",
        "-o", str(FAB / "assembly_front.pdf"), str(BOARD))
    run("pcb", "export", "pdf", "--layers", "B.Fab,Edge.Cuts,B.Silkscreen", "--mirror", "--include-border-title",
        "-o", str(FAB / "assembly_back.pdf"), str(BOARD))


def boms():
    groups = {}
    for p in D.PARTS:
        if not p["mpn"]:
            continue
        key = p["mpn"]
        g = groups.setdefault(key, dict(refs=[], value=p["value"], fp=p["fp"], mfr=p["mfr"], sides=set()))
        g["refs"].append(p["ref"]); g["sides"].add(p["side"])
    order = lambda r: (r.rstrip("0123456789"), int("".join(c for c in r if c.isdigit()) or 0))  # noqa: E731
    with open(FAB / "bom_jlcpcb.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "Manufacturer", "Manufacturer Part Number", "Quantity"])
        for mpn, g in sorted(groups.items(), key=lambda kv: order(sorted(kv[1]["refs"], key=order)[0])):
            refs = sorted(g["refs"], key=order)
            w.writerow([g["value"], ",".join(refs), g["fp"], g["mfr"], mpn, len(refs)])
    total = 0.0
    with open(FAB / "bom_distributors.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Vendor", "Vendor part number", "Manufacturer", "MPN", "Description", "Qty per board",
                    "Qty to order (5 boards)", "Unit price USD", "Line total (1 board)", "Price checked", "Stock seen",
                    "Designators", "Link", "Datasheet"])
        rows = []
        for mpn, g in groups.items():
            vendor, vpn, price, stock, checked, ds, desc = SRC.S[mpn]
            n = len(g["refs"])
            to_order = n * 5 + (2 if price < 0.5 else 0)       # spares for tiny passives
            rows.append([vendor, vpn, g["mfr"], mpn, desc, n, to_order, f"{price:.2f}", f"{price * n:.2f}", checked,
                         "" if stock is None else stock, " ".join(sorted(g["refs"], key=order)), SRC.link(mpn), ds])
            total += price * n
        disp = SRC.S["NHD-2.4-240320AF-CSXP"]
        rows.append([disp[0], disp[1], "Newhaven Display", "NHD-2.4-240320AF-CSXP", disp[6], 1, 5, f"{disp[2]:.2f}",
                     f"{disp[2]:.2f}", disp[4], disp[3], "(display, plugs into J3)", SRC.link("NHD-2.4-240320AF-CSXP"), disp[5]])
        total += disp[2]
        for item, qty, vendor, pn, price, note in SRC.EXTRA:
            rows.append([vendor, pn, "", "", item, qty, qty * 5, f"{price:.2f}", f"{price * qty:.2f}",
                         "2026-09-30" if vendor == "Mouser" else "estimate", "", note, "", ""])
            total += price * qty
        rows.sort(key=lambda r: (r[0] != "Mouser", r[0], r[3]))
        for r in rows:
            w.writerow(r)
    return total, len(groups)


def cpl():
    tmp = FAB / "pos_raw.csv"
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--use-drill-file-origin",
        "-o", str(tmp), str(BOARD))
    with open(tmp) as f, open(FAB / "cpl_jlcpcb.csv", "w", newline="") as g:
        r = csv.DictReader(f)
        w = csv.writer(g)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        n = 0
        for row in r:
            if row["Ref"].startswith(("FID", "H", "J4", "J5")):
                continue
            w.writerow([row["Ref"], f'{float(row["PosX"]):.3f}mm', f'{float(row["PosY"]):.3f}mm',
                        "Top" if row["Side"] == "top" else "Bottom", f'{float(row["Rot"]):.1f}'])
            n += 1
    tmp.unlink()
    return n


if __name__ == "__main__":
    FAB.mkdir(exist_ok=True)
    files = gerbers()
    assembly_pdfs()
    total, lines = boms()
    n = cpl()
    print("gerbers:", ", ".join(files))
    print(f"BOM: {lines} board lines, parts cost for one unit ~${total:.2f}; CPL: {n} placements")
