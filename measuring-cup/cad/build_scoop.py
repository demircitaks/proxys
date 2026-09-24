#!/usr/bin/env python3
"""Toz olcegi: STL uretimi + dogrulama raporu.

Her uretimde su olculur ve rapora yazilir:
  - her parcanin kapali (watertight) kati olmasi,
  - kapagin TUM stroku boyunca govdeye/sapa/huniye carpmamasi,
  - gozenegin acilis acisina gore gercekten ne kadar acildigi,
  - her parcanin BASKI YONUNDE desteksiz basilabilirligi,
  - hacim kalibrasyonu.
"""
import json
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as g            # noqa: E402
import kinematics as K      # noqa: E402
import scoop as S           # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl", "toz-olcegi")
DOCS = os.path.join(ROOT, "docs")

COL = dict(hazne=(196, 96, 58), kapak=(60, 150, 95), sap=(125, 90, 166),
           huni=(55, 105, 155), mil=(150, 150, 155))


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
    m.visual.face_colors = np.tile(np.array(list(c) + [255], np.uint8),
                                   (len(m.faces), 1))
    return m


def verify(p=S.P):
    out = {}
    hatch = S.build_hatch(p)
    handle = S.build_handle(p)
    funnel = S.build_funnel(p)
    ax, ad = S.hinge_axis(p)

    # --- carpisma taramasi -------------------------------------------------
    clash = {}
    for size in S.SIZES:
        body = S.build_body(size, p)
        worst = 0.0
        for a in np.arange(0.0, p["OPEN_DEG"] + 0.01, 2.5):
            hm = K.rotate_about(hatch, ax, ad, -a)
            for part in (body, handle, funnel):
                v = abs(g.inter(part, hm).volume)
                worst = max(worst, 0.0 if v != v else v)
        clash["%d mL" % size] = round(worst, 4)
    out["kapak_carpisma_mm3"] = clash
    out["sap_hazne_tirnak_mm3"] = round(
        abs(g.inter(S.build_body(15, p), handle).volume), 3)

    # --- gozenek acikligi --------------------------------------------------
    from shapely.geometry import Point
    bore = Point(0, 0).buffer(p["BORE"] / 2, resolution=128)
    opens = {}
    for a in (30, 45, 55, 65):
        o, t, pc = K.open_area(hatch, bore, ax, ad, -a)
        opens["%d derece" % a] = dict(acik_mm2=round(o, 1), yuzde=round(pc, 1))
    out["gozenek"] = opens
    out["supurme_derinligi_mm"] = round(
        K.swept_envelope_depth(hatch, ax, ad, np.arange(0, -p["OPEN_DEG"] - 1, -5)), 1)

    # --- baski yonu --------------------------------------------------------
    oh = {}
    for nm, m in (("hazne", on_bed(flip(S.build_body(15, p)))), ("kapak", on_bed(flip(hatch))),
                  ("sap", on_bed(handle)), ("huni", on_bed(flip(funnel)))):
        r = K.overhang_report(m)
        oh[nm] = dict(sorunlu_mm2=round(r["sorunlu_alan"], 1),
                      yuzde=round(100 * r["sorunlu_oran"], 2),
                      koprü_mm2=round(r["yatay_tavan"], 1))
    out["baski_cikintilari"] = oh

    # --- hacim -------------------------------------------------------------
    out["kalibrasyon"] = [dict(ml=r["ml"], derinlik_mm=round(r["depth"], 2),
                               h_bolu_D=round(r["hd"], 2),
                               olculen_ml=round(r["check"], 4),
                               agiz_capi_mm=round(r["rim_d"], 2))
                          for r in S.report(p)]
    # --- yay stroku --------------------------------------------------------
    xs = (p["SEAT_X0"] + p["SEAT_X1"]) / 2.0 - p["HINGE_X"]
    th = np.radians(-p["OPEN_DEG"])
    z2 = -xs * np.sin(th) + p["SEAT_Z"] * np.cos(th)
    out["yay"] = dict(tabla_yukselisi_mm=round(z2 - p["SEAT_Z"], 2),
                      montaj_boyu_mm=round(p["SPR_TOP"] - p["SEAT_Z"], 1),
                      tam_acikta_mm=round(p["SPR_TOP"] - z2, 1),
                      serbest_boy_mm=p["SPR_FREE"])
    # --- tetik stroku ------------------------------------------------------
    r_tip = np.hypot((p["BTN_X0"] + p["BTN_X1"]) / 2.0 - p["HINGE_X"], p["BTN_Z"])
    out["tetik_stroku_mm"] = round(2 * r_tip * np.sin(np.radians(p["OPEN_DEG"] / 2)), 1)
    # --- doz kutlesi -------------------------------------------------------
    out["doz_kutlesi_g"] = {("%d mL" % v): [round(v * 0.35, 1), round(v * 0.55, 1)]
                            for v in S.SIZES}
    return out


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    parts = [
        ("01-hazne-15ml.stl", on_bed(flip(S.build_body(15))), "hazne",
         "Baski: AGIZ TABLADA (dosya bu yonde kaydedildi)."),
        ("01-hazne-30ml.stl", on_bed(flip(S.build_body(30))), "hazne",
         "Baski: AGIZ TABLADA."),
        ("02-kapak-tetik.stl", on_bed(flip(S.build_hatch())), "kapak",
         "Baski: SIZDIRMAZ YUZ TABLADA -> yuzey birinci katman kadar duz olur."),
        ("03-sap.stl", on_bed(S.build_handle()), "sap",
         "Baski: BILEZIK TABLADA. 15/30 mL ortak."),
        ("04-huni-pet.stl", on_bed(flip(S.build_funnel())), "huni",
         "Baski: AGIZ TABLADA. Sadece 15 mL dozu icin."),
        ("05-mentese-mili.stl", on_bed(S.build_pin()), "mil",
         "Baski: dik. 3 mm celik cubuk veya M3 vida da kullanilabilir."),
    ]
    report = {"parametreler": dict(S.P), "parcalar": []}
    for name, mesh, kind, note in parts:
        assert mesh.is_volume, "%s kapali kati degil" % name
        mesh.export(os.path.join(STL, name))
        report["parcalar"].append(dict(dosya=name, tur=kind, not_=note,
                                       hacim_cm3=round(mesh.volume / 1000.0, 2),
                                       olcu_mm=[round(float(x), 1) for x in mesh.extents]))
        print("%-22s %6.2f cm3  %s mm" % (name, mesh.volume / 1000.0,
                                          np.round(mesh.extents, 1)))
    report["dogrulama"] = verify()
    with open(os.path.join(DOCS, "toz-olcegi-rapor.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    if render_png:
        import render
        render.render_row([S.build_body(15), S.build_hatch(), S.build_handle(),
                           S.build_funnel()],
                          os.path.join(DOCS, "toz-parcalar.png"), size=470,
                          colors=[COL["hazne"], COL["kapak"], COL["sap"], COL["huni"]],
                          elev=22, azim=35)
        body, handle, funnel = S.build_body(15), S.build_handle(), S.build_funnel()
        for nm, op, el in (("kapali", False, 18), ("acik", True, 18), ("alt", False, -28)):
            h = S.build_hatch(opened=op)
            asm = trimesh.util.concatenate([paint(body, COL["hazne"]),
                                            paint(h, COL["kapak"]),
                                            paint(handle, COL["sap"])])
            render.render(asm, os.path.join(DOCS, "toz-olcegi-%s.png" % nm),
                          size=760, elev=el, azim=42, color=None)
        h = S.build_hatch(opened=True)
        full = trimesh.util.concatenate([paint(body, COL["hazne"]), paint(h, COL["kapak"]),
                                         paint(handle, COL["sap"]),
                                         paint(funnel, COL["huni"])])
        render.render(full, os.path.join(DOCS, "toz-olcegi-huni.png"),
                      size=800, elev=12, azim=42, color=None)
    print("\nSTL -> %s" % STL)
    return report


if __name__ == "__main__":
    r = main(render_png="--no-render" not in sys.argv)
    print(json.dumps(r["dogrulama"], ensure_ascii=False, indent=1))
