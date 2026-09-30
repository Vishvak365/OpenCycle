"""Generate docs/sourcing/bom-v0.2.md from pcb/design.py + pcb/sourcing.py (do not edit the .md by hand).

python tools/gen_bom_md.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pcb"))
import design as D  # noqa: E402
import sourcing as SRC  # noqa: E402

GROUPS = [
    ("Radios and GPS", ["U1", "U2", "U3", "AE1"]),
    ("Display and backlight", ["J3", "Q1", "R5", "R6", "R7", "R8", "R9", "R10"]),
    ("Power, USB, battery", ["J1", "D2", "R11", "R12", "R13", "R14", "U6", "R15", "J2", "Q2", "U5", "D1", "R2",
                             "R16", "R17", "R18", "R19"]),
    ("Sensors", ["U4", "U8", "R3", "R4"]),
    ("Audio", ["U7", "R20", "LS1"]),
    ("Keys", ["SW1", "SW2", "SW3", "SW4", "SW5", "R21", "R22", "R23", "R24", "R25", "R1"]),
    ("Capacitors", [p["ref"] for p in D.PARTS if p["ref"].startswith("C")]),
]


def order(r):
    return (r.rstrip("0123456789"), int("".join(c for c in r if c.isdigit()) or 0))


def main():
    parts = {p["ref"]: p for p in D.PARTS}
    done = set()
    out = ["# Bill of materials — board v0.2 (colour build)\n\n",
           "_Generated from `pcb/design.py` + `pcb/sourcing.py` by `tools/gen_bom_md.py`. Do not edit by hand._\n\n",
           "Prices are quantity-1 USD. **Checked** = read from the distributor on that date; **typical** = commodity part "
           "stocked in the millions, price not re-read. Stock moves daily: check the cart before you order.\n\n",
           "Machine-readable versions: [`pcb/fab/bom_distributors.csv`](../../pcb/fab/bom_distributors.csv) (order list) and "
           "[`pcb/fab/bom_jlcpcb.csv`](../../pcb/fab/bom_jlcpcb.csv) (assembly).\n"]
    total = 0.0
    per_vendor = {}
    for title, refs in GROUPS:
        rows = {}
        for r in refs:
            p = parts.get(r)
            if not p or not p["mpn"] or r in done:
                continue
            done.add(r)
            rows.setdefault(p["mpn"], []).append(r)
        if not rows:
            continue
        out.append(f"\n## {title}\n\n| Refs | Qty | Part | MPN | Buy | Price | Checked | Notes |\n|---|---|---|---|---|---|---|---|\n")
        for mpn, rs in sorted(rows.items(), key=lambda kv: order(sorted(kv[1], key=order)[0])):
            vendor, vpn, price, stock, checked, ds, desc = SRC.S[mpn]
            n = len(rs)
            total += price * n
            per_vendor[vendor] = per_vendor.get(vendor, 0) + price * n
            p = parts[rs[0]]
            note = p["note"].replace("|", "/")
            st = f", {stock:,} in stock" if stock else ""
            dsl = f" · [datasheet]({ds})" if ds else ""
            out.append(f"| {', '.join(sorted(rs, key=order))} | {n} | {desc} | `{mpn}` | [{vendor} {vpn}]({SRC.link(mpn)}){dsl} "
                       f"| ${price:.2f} | {checked}{st} | {note} |\n")
    disp = SRC.S["NHD-2.4-240320AF-CSXP"]
    out.append("\n## Off the board\n\n| Item | Qty | Buy | Price | Notes |\n|---|---|---|---|---|\n")
    out.append(f"| {disp[6]} | 1 | [Mouser {disp[1]}]({SRC.link('NHD-2.4-240320AF-CSXP')}) · [datasheet]({disp[5]}) | ${disp[2]:.2f} "
               f"| checked {disp[4]}, {disp[3]:,} in stock. Plugs into J3. |\n")
    total += disp[2]; per_vendor["Mouser"] += disp[2]
    for item, qty, vendor, pn, price, note in SRC.EXTRA:
        buy = f"{vendor} {pn}".strip()
        out.append(f"| {item} | {qty} | {buy} | ${price:.2f} | {note} |\n")
        total += price * qty
        per_vendor[vendor] = per_vendor.get(vendor, 0) + price * qty
    out.append("\n## Cost for one unit (parts only)\n\n| Vendor | Subtotal |\n|---|---|\n")
    for v, t in sorted(per_vendor.items(), key=lambda kv: -kv[1]):
        out.append(f"| {v} | ${t:.2f} |\n")
    out.append(f"| **Total** | **${total:.2f}** |\n")
    out.append("\nNot included: PCBs (JLCPCB, 5 boards 4-layer 1.0 mm ≈ $15–25 + shipping), stencil (≈ $8), "
               "tools (see [instructions/01-order-parts.md](../../instructions/01-order-parts.md)).\n")
    (ROOT / "docs" / "sourcing" / "bom-v0.2.md").write_text("".join(out))
    print(f"wrote docs/sourcing/bom-v0.2.md, total ${total:.2f}")


if __name__ == "__main__":
    main()
