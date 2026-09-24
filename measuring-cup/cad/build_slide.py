#!/usr/bin/env python3
"""Surgulu toz olcegi: STL + dogrulama raporu + gorseller."""
import json
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as g              # noqa: E402
import kinematics as K        # noqa: E402
import scoop_slide as S       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "toz-surgulu")
DOCS = os.path.join(ROOT, "docs")
COL = dict(hazne=(196, 96, 58), surgu=(60, 150, 95), sap=(125, 90, 166), huni=(55, 105, 155))


def flip(m):
    m = m.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
    return m


def on_bed(m):
    m = m.copy()
    m.apply_translation((0, 0, -m.bounds[0][2]))
    return m


def paint(m, c):
    m = m.copy()
    m.visual.face_colors = np.tile(np.array(list(c) + [255], np.uint8), (len(m.faces), 1))
    return m


def verify(p=S.P):
    out = {}
    sl, sap, fun = S.build_slider(p), S.build_handle(p), S.build_funnel(p)
    bodies = {s: S.build_body(s, p) for s in S.SIZES}
    worst = {}
    for s, b in bodies.items():
        w = 0.0
        for d in np.arange(0.0, p["TRAVEL"] + 0.01, 1.0):
            m = sl.copy(); m.apply_translation((d, 0, 0))
            for part in (b, sap, fun):
                v = abs(g.inter(part, m).volume)
                w = max(w, 0.0 if v != v else v)
        worst["%d mL" % s] = round(w, 4)
    out["surgu_carpisma_mm3"] = worst
    out["sap_hazne_mm3"] = round(abs(g.inter(bodies[15], sap).volume), 3)
    out["huni_hazne_mm3"] = round(abs(g.inter(bodies[15], fun).volume), 3)
    opens = {}
    for d in (10, 18, 26):
        o, t = S.open_fraction(p, d)
        opens["%d mm" % d] = dict(acik_mm2=round(o, 1), yuzde=round(100 * o / t, 1))
    out["gozenek"] = opens
    oh = {}
    for nm, m in (("hazne", on_bed(flip(bodies[15]))), ("surgu", on_bed(sl)),
                  ("sap", on_bed(sap)), ("huni", on_bed(flip(fun)))):
        r = K.overhang_report(m)
        oh[nm] = dict(sorunlu_mm2=round(r["sorunlu_alan"], 1), yuzde=round(100 * r["sorunlu_oran"], 2),
                      koprü_mm2=round(r["yatay_tavan"], 1))
    out["baski_cikintilari"] = oh
    out["kalibrasyon"] = [dict(ml=r["ml"], derinlik_mm=round(r["depth"], 2), h_bolu_D=round(r["hd"], 2),
                               olculen_ml=round(r["check"], 4), agiz_capi_mm=round(r["rim_d"], 2))
                          for r in S.report(p)]
    out["kepce_alti_mm"] = round(-(p["PLATE_T"] + p["FIT"] + p["LIP_T"]), 2)
    out["doz_kutlesi_g"] = {"%d mL" % v: [round(v * 0.35, 1), round(v * 0.55, 1)] for v in S.SIZES}
    return out


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    parts = [
        ("01-hazne-15ml.stl", on_bed(flip(S.build_body(15))), "Baski: AGIZ TABLADA."),
        ("01-hazne-30ml.stl", on_bed(flip(S.build_body(30))), "Baski: AGIZ TABLADA."),
        ("02-surgu.stl", on_bed(S.build_slider()), "Baski: PLAKA TABLADA; uzengi catisi 33 mm koprü -> koprü ayarlari acik."),
        ("03-sap.stl", on_bed(S.build_handle()), "Baski: BILEZIK TABLADA. 15/30 mL ortak."),
        ("04-huni-pet.stl", on_bed(flip(S.build_funnel())), "Baski: AGIZ TABLADA. 15 mL / pet sise."),
    ]
    report = {"parametreler": dict(S.P), "parcalar": []}
    for name, mesh, note in parts:
        assert mesh.is_volume, name
        mesh.export(os.path.join(STL, name))
        report["parcalar"].append(dict(dosya=name, not_=note, hacim_cm3=round(mesh.volume / 1000, 2),
                                       olcu_mm=[round(float(x), 1) for x in mesh.extents]))
        print("%-20s %6.2f cm3  %s" % (name, mesh.volume / 1000, np.round(mesh.extents, 1)))
    report["dogrulama"] = verify()
    with open(os.path.join(DOCS, "toz-surgulu-rapor.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    if render_png:
        import render
        from PIL import Image, ImageDraw
        sap, fun = S.build_handle(), S.build_funnel()
        views = [("izometrik", 22, 40), ("on", 8, 180), ("sag yan", 8, 90), ("sol yan", 8, -90),
                 ("arka", 8, 0), ("ust", 88, 40), ("alt", -88, 40), ("alt-izometrik", -28, 30)]
        for size in S.SIZES:
            body = S.build_body(size)
            for state, op in (("kapali", False), ("acik", True)):
                sl = S.build_slider(opened=op)
                asm = trimesh.util.concatenate([paint(body, COL["hazne"]), paint(sl, COL["surgu"]),
                                                paint(sap, COL["sap"])])
                tiles = []
                for nm, el, az in views:
                    pth = "/tmp/sv.png"
                    render.render(asm, pth, size=420, elev=el, azim=az, color=None)
                    im = Image.open(pth); ImageDraw.Draw(im).text((10, 8), nm, fill=(40, 40, 40))
                    tiles.append(im)
                grid = Image.new("RGB", (420 * 4, 420 * 2), (250, 250, 248))
                for i, t in enumerate(tiles):
                    grid.paste(t, ((i % 4) * 420, (i // 4) * 420))
                grid.save(os.path.join(DOCS, "surgulu-%dml-%s.png" % (size, state)))
        body = S.build_body(15)
        full = trimesh.util.concatenate([paint(body, COL["hazne"]), paint(S.build_slider(opened=True), COL["surgu"]),
                                         paint(sap, COL["sap"]), paint(fun, COL["huni"])])
        render.render(full, os.path.join(DOCS, "surgulu-huni.png"), size=760, elev=12, azim=40, color=None)
        render.render_row([S.build_body(15), S.build_slider(), sap, fun],
                          os.path.join(DOCS, "surgulu-parcalar.png"), size=470,
                          colors=[COL["hazne"], COL["surgu"], COL["sap"], COL["huni"]], elev=22, azim=35)
    print("STL ->", STL)
    return report


if __name__ == "__main__":
    r = main(render_png="--no-render" not in sys.argv)
    print(json.dumps(r["dogrulama"], ensure_ascii=False, indent=1))
