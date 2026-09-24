#!/usr/bin/env python3
"""Tum parcalari uretir: STL (baski yonunde), kesit cizimleri ve onizlemeler.

Kullanim:  python3 cad/build.py [--no-render]
"""
import json
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as g            # noqa: E402
import model as M           # noqa: E402
import section              # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "stl")
DOCS = os.path.join(ROOT, "docs")

COLORS = dict(govde=(196, 96, 58), platform=(60, 150, 95), agiz=(55, 105, 155),
              kopru=(125, 90, 166), yay=(150, 150, 155), altlik=(150, 150, 155))


def flip(mesh):
    """Parcayi X ekseninde 180 derece cevirir (baski yonu icin)."""
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
    return m


def on_bed(mesh):
    m = mesh.copy()
    m.apply_translation((0, 0, -m.bounds[0][2]))
    return m


def export(mesh, name):
    path = os.path.join(STL, name)
    mesh.export(path)
    return path


def main(render_png=True):
    os.makedirs(STL, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    report = {"parametreler": {k: v for k, v in M.P.items()}, "parcalar": [],
              "kalibrasyon": []}

    parts = []
    for size in (15, 30):
        parts.append(("01-govde-%dml.stl" % size, on_bed(M.build_body(size)), "govde",
                      "Baski yonu: agiz YUKARI. Destek yok, brim onerilir."))
        parts.append(("02-platform-mil-%dml.stl" % size,
                      on_bed(flip(M.build_poppet(size))), "platform",
                      "Baski yonu: DUGME TABANDA (mil yukari). Destek yok, brim sart."))
    parts.append(("03-bosaltma-agzi.stl", on_bed(flip(M.build_base())), "agiz",
                  "Baski yonu: BORU YUKARI. Destek yok, brim onerilir."))
    parts.append(("04-kopru.stl", on_bed(M.build_yoke(15)), "kopru",
                  "Baski yonu: BILEZIK TABANDA. Destek yok. 15/30 mL ortak."))
    parts.append(("05-yay-baskili.stl", on_bed(M.build_spring()), "yay",
                  "Opsiyonel: metal yay yerine. 0.2 mm katman, 100% dolgu."))
    parts.append(("06-altlik.stl", on_bed(M.build_stand()), "altlik",
                  "Opsiyonel: dik durma + damla tutucu. Destek yok."))

    for name, mesh, kind, note in parts:
        assert mesh.is_volume, "%s kapali bir kati degil" % name
        export(mesh, name)
        report["parcalar"].append(dict(
            dosya=name, tur=kind, not_=note,
            hacim_cm3=round(mesh.volume / 1000.0, 2),
            olcu_mm=[round(float(x), 1) for x in mesh.extents],
            su_gecirmez=bool(mesh.is_volume), yuzey=int(len(mesh.faces))))
        print("%-26s %6.2f cm3  %s mm" % (name, mesh.volume / 1000.0,
                                          np.round(mesh.extents, 1)))

    for r in M.geometry_report():
        report["kalibrasyon"].append(dict(
            boy_ml=r["size"], dolum_yuksekligi_mm=round(r["h_max"], 2),
            agiz_yuksekligi_mm=round(r["rim"], 2),
            olculen_hacim_ml=round(r["check"], 4),
            cizgiler={str(m): round(z, 2) for m, z in r["marks"]}))

    # --- girisim kontrolu ---------------------------------------------------
    report["girisim_mm3"] = {}
    for size in (15, 30):
        for st in (False, True):
            key = "%dml-%s" % (size, "acik" if st else "kapali")
            vals = {k: (0.0 if v != v else round(float(v), 3))
                    for k, v in M.interference(size, open_valve=st).items()}
            report["girisim_mm3"][key] = {k: v for k, v in vals.items() if v > 0.01}

    with open(os.path.join(DOCS, "rapor.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    for size in (15, 30):
        open(os.path.join(DOCS, "kesit-%dml.svg" % size), "w").write(
            section.draw(size))

    if render_png:
        import render
        render.render_row(
            [M.build_body(15), M.build_poppet(15), M.build_base(), M.build_yoke(15),
             M.build_stand()],
            os.path.join(DOCS, "parcalar.png"), size=480,
            colors=[COLORS["govde"], COLORS["platform"], COLORS["agiz"],
                    COLORS["kopru"], COLORS["altlik"]])
        for size in (15, 30):
            asm = M.assembled(size)
            cols = dict(body=COLORS["govde"], poppet=COLORS["platform"],
                        base=COLORS["agiz"], yoke=COLORS["kopru"],
                        spring=COLORS["yay"])
            merged = trimesh.util.concatenate([
                _paint(asm[k], cols[k]) for k in ("body", "base", "poppet", "yoke",
                                                  "spring")])
            render.render(merged, os.path.join(DOCS, "montaj-%dml.png" % size),
                          size=800, elev=18, azim=34, color=None)
    print("\nSTL -> %s\ndokuman -> %s" % (STL, DOCS))
    return report


def _paint(mesh, rgb):
    m = mesh.copy()
    m.visual.face_colors = np.tile(np.array(list(rgb) + [255], np.uint8),
                                   (len(m.faces), 1))
    return m


if __name__ == "__main__":
    main(render_png="--no-render" not in sys.argv)
