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
    hole = g.cyl(p["HOLE_D"] / 2, 0.5, 4.0)
    for size in S.SIZES:
        pl, pl0 = S.build_plate(size, p), S.build_plate(size, p, bumps=False)
        c, c0, cap = S.build_cup(size, p), S.build_cup(size, p, pockets=False), S.build_cap(size, p)
        w = wb = 0.0
        for dx in np.arange(0.5, p["TRAVEL"] + 0.01, 0.5):
            m0 = pl0.copy(); m0.apply_translation((dx, 0, 0)); w = max(w, iv(c0, m0))
            m = pl.copy(); m.apply_translation((dx, 0, 0)); wb = max(wb, iv(c, m))
        po = S.build_plate(size, p, opened=True)
        d = S.dims(size, p)
        out["%d mL" % size] = dict(surgu_kayma_mm3=round(w, 3), centik_esneme_mm3=round(wb, 3),
                                   kapali_mm3=round(iv(c, pl), 3), acik_mm3=round(iv(c, po), 3),
                                   ust_kapak_mm3=round(iv(c, cap), 3), kapak_surgu_mm3=round(max(iv(cap, pl), iv(cap, po)), 3),
                                   acikken_delik_ortusu_mm3=round(iv(po, hole), 3),
                                   kapaliyken_delik_ortusu_oran=round(iv(pl, hole) / (np.pi * (p["HOLE_D"] / 2) ** 2 * p["PL_T"]), 3),
                                   derinlik_mm=round(d["depth"], 2), yukseklik_mm=round(d["H"], 2),
                                   hacim_ml=round((S._fun_vol(p) + S.B.brim_volume(d["depth"] - d["fun_h"], dict(S.B.P, BORE=2 * p["FUN_R1"], DRAFT=p["DRAFT"]))) / 1000, 4))
    oh = {}
    for nm, m in (("hazne_15", on_bed(flip(S.build_cup(15, p)))), ("hazne_30", on_bed(flip(S.build_cup(30, p)))),
                  ("surgu_15", on_bed(S.build_plate(15, p))), ("surgu_30", on_bed(S.build_plate(30, p))),
                  ("ust_kapak_15", on_bed(flip(S.build_cap(15, p))))):
        r = K.overhang_report(m)
        oh[nm] = dict(sorunlu_mm2=round(r["sorunlu_alan"], 1), yuzde=round(100 * r["sorunlu_oran"], 2), koprü_mm2=round(r["yatay_tavan"], 1))
    out["baski_cikintilari"] = oh
    return out


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    parts = [("01-hazne-15ml.stl", on_bed(flip(S.build_cup(15))), "Baski: AGIZ TABLADA (ters), sap tablada, huni yukari. Destek yok."),
             ("01-hazne-30ml.stl", on_bed(flip(S.build_cup(30))), "Baski: AGIZ TABLADA (ters), sap tablada."),
             ("02-surgu-15ml.stl", on_bed(S.build_plate(15)), "Baski: PLAKA TABLADA, ayak dik."),
             ("02-surgu-30ml.stl", on_bed(S.build_plate(30)), "Baski: PLAKA TABLADA, ayak dik."),
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
                parts3 = [paint(cup, COL["h"]), paint(S.build_plate(size, opened=op), COL["p"])]
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
        render.render_row([S.build_cup(15), S.build_plate(15), flip(S.build_cap(15))],
                          os.path.join(DOCS, "mini-parcalar.png"), size=440, colors=[COL["h"], COL["p"], COL["l"]], elev=22, azim=35)
        hero = trimesh.util.concatenate([paint(S.build_cup(15), COL["h"]), paint(S.build_plate(15), COL["p"]), paint(S.build_cap(15), COL["l"])])
        render.render(hero, os.path.join(DOCS, "mini-kepce.png"), size=800, elev=24, azim=35, color=None)
        # acik: ust kapak yok, surgu cekilmis, alttan bakis
        hero2 = trimesh.util.concatenate([paint(S.build_cup(15), COL["h"]), paint(S.build_plate(15, opened=True), COL["p"])])
        render.render(hero2, os.path.join(DOCS, "mini-acik-alt.png"), size=800, elev=-30, azim=35, color=None)
    print("STL ->", STL)
    return report


if __name__ == "__main__":
    r = main(render_png="--no-render" not in sys.argv)
    print(json.dumps(r["dogrulama"], ensure_ascii=False, indent=1))
