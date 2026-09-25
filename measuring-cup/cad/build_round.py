#!/usr/bin/env python3
"""Sade surmeli kepce: STL + dogrulama + gorseller."""
import json, os, sys
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as g, kinematics as K, scoop_round as S   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "toz-yuvarlak"); DOCS = os.path.join(ROOT, "docs")
COL = dict(h=(196, 96, 58), p=(60, 150, 95), l=(220, 180, 60), f=(55, 105, 155))


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
    for size in S.SIZES:
        b, b0 = S.build_body(size, p), S.build_body(size, p, bumps=False)
        top, top0 = S.build_top(size, p), S.build_top(size, p, bump=False)
        pl, pl0 = S.build_plate(size, p), S.build_plate(size, p, notches=False)
        wp = wpb = 0.0
        for dx in np.arange(0.5, p["TRAVEL"] + 8.01, 0.5):
            m0 = pl0.copy(); m0.apply_translation((dx, 0, 0)); wp = max(wp, iv(b0, m0))
            m = pl.copy(); m.apply_translation((dx, 0, 0)); wpb = max(wpb, iv(b, m))
        wt = wtb = wpt = 0.0
        for a in np.arange(1.0, p["OPEN_DEG"] + 0.01, 1.0):
            mt = S._rot(top0, -a, p)
            wt = max(wt, iv(b0, mt)); wtb = max(wtb, iv(b, S._rot(top, -a, p)))
            po = S.build_plate(size, p, opened=True); wpt = max(wpt, iv(po, mt))
        out["%d mL" % size] = dict(plaka_kayma_mm3=round(wp, 3), ust_kapak_donus_mm3=round(wt, 3),
                                   plaka_ust_kapak_mm3=round(wpt, 3),
                                   plaka_tumsek_girisim_mm3=round(wpb, 3), ust_tumsek_girisim_mm3=round(wtb, 3),
                                   kapali_plaka_mm3=round(iv(b, pl), 3), kapali_ust_mm3=round(iv(b, top), 3),
                                   acik_plaka_mm3=round(iv(b, S.build_plate(size, p, opened=True)), 3))
    oh = {}
    for nm, m in (("hazne_15", on_bed(flip(S.build_body(15, p)))), ("hazne_30", on_bed(flip(S.build_body(30, p)))),
                  ("plaka_15", on_bed(S.build_plate(15, p))), ("plaka_30", on_bed(S.build_plate(30, p))),
                  ("ust_disk", on_bed(flip(S.build_top(15, p)))), ("mil", on_bed(S.build_pin(15, p)))):
        r = K.overhang_report(m)
        oh[nm] = dict(sorunlu_mm2=round(r["sorunlu_alan"], 1), yuzde=round(100 * r["sorunlu_oran"], 2), koprü_mm2=round(r["yatay_tavan"], 1))
    out["baski_cikintilari"] = oh
    out["kalibrasyon"] = [dict(ml=r["ml"], derinlik_mm=round(r["depth"], 2), olculen_ml=round(r["check"], 4)) for r in S.report(p)]
    return out


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    parts = [("01-hazne-15ml.stl", on_bed(flip(S.build_body(15))), "Baski: AGIZ TABLADA (ters), huni yukari. Destek yok."),
             ("01-hazne-30ml.stl", on_bed(flip(S.build_body(30))), "Baski: AGIZ TABLADA (ters), huni yukari."),
             ("02-alt-plaka-15ml.stl", on_bed(S.build_plate(15)), "Baski: PLAKA ALTI TABLADA, cikintilar yukari; conta yuzu utulenir."),
             ("02-alt-plaka-30ml.stl", on_bed(S.build_plate(30)), "Baski: PLAKA ALTI TABLADA; conta yuzu utulenir."),
             ("03-ust-disk-15ml.stl", on_bed(flip(S.build_top(15))), "Baski: UST YUZ TABLADA (bacak/parmak yukari)."),
             ("03-ust-disk-30ml.stl", on_bed(flip(S.build_top(30))), "Baski: UST YUZ TABLADA (bacak/parmak yukari)."),
             ("04-mil-15ml.stl", on_bed(S.build_pin(15)), "Baski: BAS TABLADA."),
             ("04-mil-30ml.stl", on_bed(S.build_pin(30)), "Baski: BAS TABLADA."),
             ("05-conta-tpu.stl", on_bed(S.build_gasket()), "Opsiyonel: O-ring yoksa TPU.")]
    report = {"parametreler": {k: v for k, v in S.P.items()}, "parcalar": []}
    for name, mesh, note in parts:
        assert mesh.is_volume, name
        mesh.export(os.path.join(STL, name))
        report["parcalar"].append(dict(dosya=name, not_=note, hacim_cm3=round(mesh.volume / 1000, 2),
                                       olcu_mm=[round(float(x), 1) for x in mesh.extents]))
        print("%-22s %6.2f cm3  %s" % (name, mesh.volume / 1000, np.round(mesh.extents, 1)))
    report["dogrulama"] = verify()
    json.dump(report, open(os.path.join(DOCS, "toz-yuvarlak-rapor.json"), "w"), indent=2, ensure_ascii=False)
    if render_png:
        import render
        from PIL import Image, ImageDraw
        views = [("izometrik", 22, 40), ("on", 8, 180), ("yan", 8, 90), ("arka", 8, 0),
                 ("ust", 88, 40), ("alt", -88, 40), ("alt-izometrik", -28, 30), ("arka-izometrik", 22, -140)]
        for size in S.SIZES:
            body = S.build_body(size); pin = S.build_pin(size); pin.apply_translation((S.P["PIVOT_X"], 0, -S.P["DISC_T"] - 1.2))
            for state in ("kapali", "acik"):
                op = state == "acik"
                asm = trimesh.util.concatenate([paint(body, COL["h"]), paint(S.build_plate(size, opened=op), COL["p"]),
                                                paint(S.build_top(size, opened=op), COL["l"]), paint(pin, (150, 150, 155))])
                tiles = []
                for nm, el, az in views:
                    render.render(asm, "/tmp/sv.png", size=420, elev=el, azim=az, color=None)
                    im = Image.open("/tmp/sv.png"); ImageDraw.Draw(im).text((10, 8), nm, fill=(40, 40, 40)); tiles.append(im)
                grid = Image.new("RGB", (420 * 4, 420 * 2), (250, 250, 248))
                for i, t in enumerate(tiles): grid.paste(t, ((i % 4) * 420, (i // 4) * 420))
                grid.save(os.path.join(DOCS, "yuvarlak-%dml-%s.png" % (size, state)))
        render.render_row([S.build_body(15), S.build_plate(15), S.build_top(15), S.build_pin(15)],
                          os.path.join(DOCS, "yuvarlak-parcalar.png"), size=440,
                          colors=[COL["h"], COL["p"], COL["l"], (150, 150, 155)], elev=22, azim=35)
        body = S.build_body(15); pin = S.build_pin(15); pin.apply_translation((S.P["PIVOT_X"], 0, -S.P["DISC_T"] - 1.2))
        hero = trimesh.util.concatenate([paint(body, COL["h"]), paint(S.build_plate(15), COL["p"]), paint(S.build_top(15), COL["l"]), paint(pin, (150, 150, 155))])
        render.render(hero, os.path.join(DOCS, "yuvarlak-kepce.png"), size=800, elev=20, azim=35, color=None)
    print("STL ->", STL)
    return report


if __name__ == "__main__":
    r = main(render_png="--no-render" not in sys.argv)
    print(json.dumps(r["dogrulama"], ensure_ascii=False, indent=1))
