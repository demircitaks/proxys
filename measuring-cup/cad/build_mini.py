#!/usr/bin/env python3
"""Mini kepce: STL + dogrulama + gorseller."""
import json, os, sys
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as g, kinematics as K, scoop_mini as S   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "toz-mini"); DOCS = os.path.join(ROOT, "docs")
COL = dict(h=(196, 96, 58), p=(60, 150, 95), l=(220, 180, 60))


def flip(m):
    m = m.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0))); return m


def on_bed(m):
    m = m.copy(); m.apply_translation((0, 0, -m.bounds[0][2])); return m


def paint(m, c):
    m = m.copy(); m.visual.face_colors = np.tile(np.array(list(c) + [255], np.uint8), (len(m.faces), 1)); return m


def iv(a, b):
    v = abs(g.inter(a, b).volume); return 0.0 if v != v else v


def verify(p=S.P):
    out = {}
    sh, sh0 = S.build_shutter(p), S.build_shutter(p, notches=False)
    for size in S.SIZES:
        c, c0, cap = S.build_cup(size, p), S.build_cup(size, p, bumps=False), S.build_cap(size, p)
        w = wb = 0.0
        for a in np.arange(1.0, 180.01, 1.0):
            w = max(w, iv(c0, g.rotz(sh0, a))); wb = max(wb, iv(c, g.rotz(sh, a)))
        d = S.dims(size, p)
        out["%d mL" % size] = dict(kapak_donus_mm3=round(w, 3), centik_esneme_mm3=round(wb, 3),
                                   acik_mm3=round(iv(c, sh), 3), kapali_mm3=round(iv(c, S.build_shutter(p, opened=False)), 3),
                                   ust_kapak_mm3=round(iv(c, cap), 3), derinlik_mm=round(d["depth"], 2),
                                   hacim_ml=round(S.B.brim_volume(d["depth"], dict(S.B.P, BORE=p["BORE"], DRAFT=p["DRAFT"])) / 1000, 4))
    oh = {}
    for nm, m in (("hazne_15", on_bed(S.build_cup(15, p))), ("hazne_30", on_bed(S.build_cup(30, p))),
                  ("taban_kapagi", on_bed(sh)), ("ust_kapak_15", on_bed(flip(S.build_cap(15, p))))):
        r = K.overhang_report(m)
        oh[nm] = dict(sorunlu_mm2=round(r["sorunlu_alan"], 1), yuzde=round(100 * r["sorunlu_oran"], 2), koprü_mm2=round(r["yatay_tavan"], 1))
    out["baski_cikintilari"] = oh
    return out


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    parts = [("01-hazne-15ml.stl", on_bed(S.build_cup(15)), "Baski: TABAN TABLADA (agiz yukari), sap tablada. Destek yok."),
             ("01-hazne-30ml.stl", on_bed(S.build_cup(30)), "Baski: TABAN TABLADA (agiz yukari)."),
             ("02-taban-kapagi.stl", on_bed(S.build_shutter()), "Baski: ALT YUZ TABLADA (duz), etek yukari. Ortak."),
             ("03-ust-kapak-15ml.stl", on_bed(flip(S.build_cap(15))), "Baski: DIS YUZU TABLADA, etek yukari."),
             ("03-ust-kapak-30ml.stl", on_bed(flip(S.build_cap(30))), "Baski: DIS YUZU TABLADA, etek yukari.")]
    report = {"parametreler": dict(S.P), "parcalar": []}
    for name, mesh, note in parts:
        assert mesh.is_volume, name
        mesh.export(os.path.join(STL, name))
        report["parcalar"].append(dict(dosya=name, not_=note, hacim_cm3=round(mesh.volume / 1000, 2),
                                       olcu_mm=[round(float(x), 1) for x in mesh.extents]))
        print("%-22s %6.2f cm3  %s" % (name, mesh.volume / 1000, np.round(mesh.extents, 1)))
    report["dogrulama"] = verify()
    json.dump(report, open(os.path.join(DOCS, "toz-mini-rapor.json"), "w"), indent=2, ensure_ascii=False)
    if render_png:
        import render
        from PIL import Image, ImageDraw
        views = [("izometrik", 22, 40), ("on", 8, 180), ("yan", 8, 90), ("ust", 88, 40),
                 ("alt", -88, 40), ("alt-izometrik", -28, 30)]
        for size in S.SIZES:
            cup = S.build_cup(size)
            for state in ("kapali", "acik"):
                op = state == "acik"
                parts3 = [paint(cup, COL["h"]), paint(S.build_shutter(opened=op), COL["p"])]
                if not op:
                    parts3.append(paint(S.build_cap(size), COL["l"]))
                asm = trimesh.util.concatenate(parts3)
                tiles = []
                for nm, el, az in views:
                    render.render(asm, "/tmp/sv.png", size=420, elev=el, azim=az, color=None)
                    im = Image.open("/tmp/sv.png"); ImageDraw.Draw(im).text((10, 8), nm, fill=(40, 40, 40)); tiles.append(im)
                grid = Image.new("RGB", (420 * 3, 420 * 2), (250, 250, 248))
                for i, t in enumerate(tiles): grid.paste(t, ((i % 3) * 420, (i // 3) * 420))
                grid.save(os.path.join(DOCS, "mini-%dml-%s.png" % (size, state)))
        render.render_row([S.build_cup(15), S.build_shutter(), flip(S.build_cap(15))],
                          os.path.join(DOCS, "mini-parcalar.png"), size=440, colors=[COL["h"], COL["p"], COL["l"]], elev=22, azim=35)
        hero = trimesh.util.concatenate([paint(S.build_cup(15), COL["h"]), paint(S.build_shutter(), COL["p"]), paint(S.build_cap(15), COL["l"])])
        render.render(hero, os.path.join(DOCS, "mini-kepce.png"), size=800, elev=24, azim=35, color=None)
        # acik: ust kapak yok, taban kapagi 180 cevrilmis, alttan bakis
        hero2 = trimesh.util.concatenate([paint(S.build_cup(15), COL["h"]), paint(S.build_shutter(opened=True), COL["p"])])
        render.render(hero2, os.path.join(DOCS, "mini-acik-alt.png"), size=800, elev=-30, azim=35, color=None)
    print("STL ->", STL)
    return report


if __name__ == "__main__":
    r = main(render_png="--no-render" not in sys.argv)
    print(json.dumps(r["dogrulama"], ensure_ascii=False, indent=1))
