"""Interference check: every pair of parts that should not touch."""
import itertools
from model import build

# pairs that are meant to touch/compress
ALLOWED = {
    frozenset({"oring", "std_front_bezel"}), frozenset({"oring", "aero_front_bezel"}),
    frozenset({"display", "display_active_area"}),
    frozenset({"tact_switches", "pcb"}), frozenset({"front_switches", "pcb"}),
    frozenset({"lens_mask", "cover_lens"}),
    frozenset({"speaker", "speaker_membrane"}),
}
TOL = 0.5  # mm3 of overlap ignored (tessellation / coincident faces)


def check(variant_shells):
    parts, shells = build()
    solids = {**parts, **{k: shells[k] for k in variant_shells}}
    bad = []
    names = list(solids)
    for a, b in itertools.combinations(names, 2):
        if frozenset({a, b}) in ALLOWED:
            continue
        ba, bb = solids[a].val().BoundingBox(), solids[b].val().BoundingBox()
        if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or
                bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin):
            continue
        v = solids[a].intersect(solids[b]).val().Volume()
        if v > TOL:
            bad.append((a, b, round(v, 2)))
    return bad


if __name__ == "__main__":
    ok = True
    for name, shells in {
        "standard": ["std_back_shell", "std_front_bezel"],
        "aero": ["aero_back_shell", "aero_front_bezel"],
        "rugged": ["std_back_shell", "std_front_bezel", "rugged_bumper", "rugged_button_covers"],
    }.items():
        bad = check(shells)
        print(f"{name}: {'OK' if not bad else bad}")
        ok &= not bad
    raise SystemExit(0 if ok else 1)
