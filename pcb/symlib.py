from kiutils.symbol import SymbolLib
import functools
LIB="/usr/share/kicad/symbols/"
@functools.lru_cache(None)
def lib(name): return SymbolLib.from_file(LIB+name+".kicad_sym")
def get(libname, sym):
    L=lib(libname)
    s=next(x for x in L.symbols if x.entryName==sym)
    if s.extends:
        base=next(x for x in L.symbols if x.entryName==s.extends)
        return s, base
    return s, s
def pins(libname, sym):
    s,base=get(libname,sym)
    out=[]
    for u in base.units:
        for p in u.pins: out.append((p.number, p.name, p.electricalType, p.position.X, p.position.Y, p.position.angle or 0, p.length))
    return out
