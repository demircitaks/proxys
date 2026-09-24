#!/usr/bin/env python3
"""Sade surmeli kepce: STL + dogrulama + gorseller."""
import json, os, sys
import numpy as np
import trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as g, kinematics as K, scoop_slim as S   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "toz-sade"); DOCS = os.path.join(ROOT, "docs")
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
    pl, fun = S.build_plate(p), S.build_funnel(p)
    for size in S.SIZES:
        b, lid = S.build_body(size, p, strut=False), S.build_lid(size, p)
        w = 0.0
        for d in np.arange(0.0, p["TRAVEL"] + 0.01, 1.0):
            m = pl.copy(); m.apply_translation((d, 0, 0))
            for part in (b, lid, fun): w = max(w, iv(part, m))
        wl, T = 0.0, S.lid_travel(size, p)
        for d in np.arange(0.0, T + 0.01, 1.0):
            m = lid.copy(); m.apply_translation((d, 0, 0))
            for part in (b, pl): wl = max(wl, iv(part, m))
        out["%d mL" % size] = dict(alt_plaka_stroku_mm3=round(w, 3), ust_kapak_stroku_mm=round(T, 1),
                                   ust_kapak_stroku_mm3=round(wl, 3), huni_hazne_mm3=round(iv(fun, b), 3),
                                   centik_kapali_alt_mm3=round(iv(b, pl), 3), centik_kapali_ust_mm3=round(iv(b, lid), 3))
    oh = {}
    for nm, m in (("hazne", on_bed(S.build_body(15, p, strut=False))), ("plaka", on_bed(flip(pl))),
                  ("kapak", on_bed(S.build_lid(15, p))), ("huni", on_bed(flip(fun)))):
        r = K.overhang_report(m)
        oh[nm] = dict(sorunlu_mm2=round(r["sorunlu_alan"], 1), yuzde=round(100 * r["sorunlu_oran"], 2), koprü_mm2=round(r["yatay_tavan"], 1))
    out["baski_cikintilari"] = oh
    o, t = S.open_fraction(p); out["alt_acik_yuzde"] = round(100 * o / t, 1)
    out["kalibrasyon"] = [dict(ml=r["ml"], derinlik_mm=round(r["depth"], 2), olculen_ml=round(r["check"], 4)) for r in S.report(p)]
    return out


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    parts = [("01-hazne-15ml.stl", on_bed(S.build_body(15)), "Baski: AGIZ YUKARI (kanal dudaklari tablada), brim."),
             ("01-hazne-30ml.stl", on_bed(S.build_body(30)), "Baski: AGIZ YUKARI, brim."),
             ("02-alt-plaka.stl", on_bed(flip(S.build_plate())), "Baski: UST (conta) YUZU TABLADA. Ortak."),
             ("03-ust-kapak-15ml.stl", on_bed(S.build_lid(15)), "Baski: ALT YUZ TABLADA."),
             ("03-ust-kapak-30ml.stl", on_bed(S.build_lid(30)), "Baski: ALT YUZ TABLADA."),
             ("04-huni-pet-vidali.stl", on_bed(flip(S.build_funnel())), "Opsiyonel. Baski: AGIZ TABLADA."),
             ("05-conta-tpu.stl", on_bed(S.build_gasket()), "Opsiyonel: O-ring yoksa TPU.")]
    report = {"parametreler": {k: v for k, v in S.P.items()}, "parcalar": []}
    for name, mesh, note in parts:
        assert mesh.is_volume or "hazne" in name, name   # hazne + payanda iki ayri kati
        mesh.export(os.path.join(STL, name))
        report["parcalar"].append(dict(dosya=name, not_=note, hacim_cm3=round(mesh.volume / 1000, 2),
                                       olcu_mm=[round(float(x), 1) for x in mesh.extents]))
        print("%-22s %6.2f cm3  %s" % (name, mesh.volume / 1000, np.round(mesh.extents, 1)))
    report["dogrulama"] = verify()
    json.dump(report, open(os.path.join(DOCS, "toz-sade-rapor.json"), "w"), indent=2, ensure_ascii=False)
    if render_png:
        import render
        from PIL import Image, ImageDraw
        views = [("izometrik", 22, 40), ("on", 8, 180), ("yan", 8, 90), ("arka", 8, 0),
                 ("ust", 88, 40), ("alt", -88, 40), ("alt-izometrik", -28, 30), ("arka-izometrik", 22, -140)]
        for size in S.SIZES:
            body = S.build_body(size, strut=False)
            for state in ("kapali", "acik"):
                op = state == "acik"
                asm = trimesh.util.concatenate([paint(body, COL["h"]), paint(S.build_plate(opened=op), COL["p"]),
                                                paint(S.build_lid(size, opened=op), COL["l"])])
                tiles = []
                for nm, el, az in views:
                    render.render(asm, "/tmp/sv.png", size=420, elev=el, azim=az, color=None)
                    im = Image.open("/tmp/sv.png"); ImageDraw.Draw(im).text((10, 8), nm, fill=(40, 40, 40)); tiles.append(im)
                grid = Image.new("RGB", (420 * 4, 420 * 2), (250, 250, 248))
                for i, t in enumerate(tiles): grid.paste(t, ((i % 4) * 420, (i // 4) * 420))
                grid.save(os.path.join(DOCS, "sade-%dml-%s.png" % (size, state)))
        render.render_row([S.build_body(15), S.build_plate(), S.build_lid(15), S.build_funnel()],
                          os.path.join(DOCS, "sade-parcalar.png"), size=460,
                          colors=[COL["h"], COL["p"], COL["l"], COL["f"]], elev=22, azim=35)
        body = S.build_body(15, strut=False)
        hero = trimesh.util.concatenate([paint(body, COL["h"]), paint(S.build_plate(), COL["p"]), paint(S.build_lid(15), COL["l"])])
        render.render(hero, os.path.join(DOCS, "sade-kepce.png"), size=800, elev=20, azim=35, color=None)
    print("STL ->", STL)
    return report


if __name__ == "__main__":
    r = main(render_png="--no-render" not in sys.argv)
    print(json.dumps(r["dogrulama"], ensure_ascii=False, indent=1))
