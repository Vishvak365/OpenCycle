#!/usr/bin/env python3
"""Build the static Inter fonts used by the Lucent UI (viewer/ui/fonts/).

Inter is OFL-1.1 (rsms/inter). Google Fonts ships it as one variable font with `opsz`
(14..32) and `wght` axes. lv_font_conv and the browser preview both want plain static TTFs,
so this script:
  1. pins the axes (Text = opsz 14, Display = opsz 32) at the weights we use,
  2. freezes tabular figures into the cmap (digits keep a fixed width, so changing numbers
     never jitter; lv_font_conv does not apply OpenType features, so this has to be baked),
  3. subsets to the glyphs the UI uses (same ranges as the lv_font_conv command in docs/UI.md).

  pip install fonttools
  python3 docs/ui/make_fonts.py            # downloads the variable font if it is not cached
"""
import os, sys, urllib.request
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'viewer', 'ui', 'fonts')
SRC_URL = 'https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf'
OFL_URL = 'https://raw.githubusercontent.com/google/fonts/main/ofl/inter/OFL.txt'
CACHE = os.environ.get('INTER_VF', os.path.join(os.environ.get('TMPDIR', '/tmp'), 'Inter-VF.ttf'))

# printable ASCII + the few symbols the UI draws (keep in sync with docs/UI.md "Type")
UNICODES = list(range(0x20, 0x7F)) + [0xA0, 0xB0, 0xB7, 0xD7, 0x2013, 0x2014, 0x2019, 0x2022, 0x2026,
                                      0x2190, 0x2191, 0x2192, 0x2193, 0x2212]
BUILDS = [  # file, family, opsz, wght
    ('Inter-Medium.ttf', 'Inter', 14, 500),
    ('Inter-SemiBold.ttf', 'Inter', 14, 600),
    ('InterDisplay-Medium.ttf', 'Inter Display', 32, 500),
    ('InterDisplay-SemiBold.ttf', 'Inter Display', 32, 600),
]


def freeze_tnum(font):
    gsub = font['GSUB'].table
    idx = {i for fr in gsub.FeatureList.FeatureRecord if fr.FeatureTag == 'tnum' for i in fr.Feature.LookupListIndex}
    mapping = {}
    for i in idx:
        for st in gsub.LookupList.Lookup[i].SubTable:
            st = getattr(st, 'ExtSubTable', st)
            if hasattr(st, 'mapping'):
                mapping.update(st.mapping)
    for table in font['cmap'].tables:
        for cp, gname in list(table.cmap.items()):
            if gname in mapping:
                table.cmap[cp] = mapping[gname]
    return len(mapping)


def main():
    if not os.path.exists(CACHE):
        print('downloading', SRC_URL)
        urllib.request.urlretrieve(SRC_URL, CACHE)
    os.makedirs(OUT, exist_ok=True)
    for fname, fam, opsz, wght in BUILDS:
        f = instantiateVariableFont(TTFont(CACHE), {'opsz': opsz, 'wght': wght}, updateFontNames=False)
        n = freeze_tnum(f)
        opts = subset.Options()
        opts.layout_features = ['kern']
        opts.name_IDs = ['*']
        opts.notdef_outline = True
        opts.hinting = False
        s = subset.Subsetter(opts)
        s.populate(unicodes=UNICODES)
        s.subset(f)
        style = 'SemiBold' if wght == 600 else 'Medium'
        for rec in f['name'].names:
            if rec.nameID in (1, 16):
                rec.string = fam
            elif rec.nameID in (2, 17):
                rec.string = style
            elif rec.nameID == 4:
                rec.string = f'{fam} {style}'
            elif rec.nameID == 6:
                rec.string = f'{fam.replace(" ", "")}-{style}'
        path = os.path.join(OUT, fname)
        f.save(path)
        print(f'{fname}: opsz {opsz} wght {wght}, {n} tnum glyphs frozen, {os.path.getsize(path)} bytes')
    urllib.request.urlretrieve(OFL_URL, os.path.join(OUT, 'OFL-Inter.txt'))


if __name__ == '__main__':
    sys.exit(main())
