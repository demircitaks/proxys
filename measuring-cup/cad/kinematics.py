"""Hareketli parca dogrulamalari: bir parcayi hareket boyunca adim adim
suruyup govdeye carpip carpmadigini ve gercekten acildigini olcer."""
import numpy as np
import trimesh

import geom as g


def rotate_about(mesh, axis_point, axis_dir, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(deg), axis_dir, axis_point))
    return m


def sweep_clearance(moving, fixed, axis_point, axis_dir, angles):
    """Her acida govde ile carpisma hacmini (mm3) dondurur."""
    out = []
    for a in angles:
        m = rotate_about(moving, axis_point, axis_dir, a)
        try:
            v = g.inter(m, fixed).volume
        except Exception:
            v = 0.0
        out.append((float(a), 0.0 if v != v else float(v)))
    return out


def shadow(mesh):
    """Parcanin XY duzlemine dusen golgesi (shapely poligonu)."""
    from trimesh.path import polygons
    return polygons.projected(mesh, normal=[0.0, 0.0, 1.0])


def open_area(moving, bore_poly, axis_point, axis_dir, deg):
    """Verilen acida gozenegin ne kadari gercekten aciktir.

    Hareketli parcanin dusey izdusumu gozenekten cikarilir.
    Donen: (acik mm2, toplam mm2, acik yuzde).
    """
    sh = shadow(rotate_about(moving, axis_point, axis_dir, deg))
    blocked = bore_poly.intersection(sh).area if sh is not None else 0.0
    total = bore_poly.area
    return total - blocked, total, 100.0 * (total - blocked) / total


def swept_envelope_depth(moving, axis_point, axis_dir, angles):
    """Hareket boyunca parcanin indigi en dusuk z (montaj alti bosluk ihtiyaci)."""
    lo = 0.0
    for a in angles:
        lo = min(lo, float(rotate_about(moving, axis_point, axis_dir, a).bounds[0][2]))
    return lo


# --------------------------------------------------------------------------
# baski yonu dogrulamasi
# --------------------------------------------------------------------------
def overhang_report(mesh, limit_deg=45.0, bridge_span=6.0):
    """Verilen baski yonunde (mesh'in +Z'si baski yonu) desteksiz basilamayacak
    yuzey alanini olcer.

    Asagi bakan bir yuzun egimi dikeyden `limit_deg`'i asiyorsa problemlidir.
    Neredeyse yatay yuzler (koprü olabilecekler) ayri raporlanir; bunlarin
    kisa acikliklari dilimleyici koprü olarak basar.
    """
    n = mesh.face_normals
    a = mesh.area_faces
    # tabla duzlemindeki yuzler baski yuzeyidir, cikinti degildir
    zmin = mesh.bounds[0][2]
    fz = mesh.vertices[mesh.faces][:, :, 2].max(axis=1)
    on_bed = fz <= zmin + 0.3
    down = (n[:, 2] < 0) & (~on_bed)
    # yuzun dikeyden sapmasi: normalin -Z ile acisi
    with np.errstate(invalid="ignore"):
        tilt = np.degrees(np.arccos(np.clip(-n[:, 2], -1.0, 1.0)))
    steep = down & (tilt < (90.0 - limit_deg))        # dikeyden > limit egimli
    flat = down & (tilt < 8.0)                        # neredeyse yatay tavan
    total_down = float(a[down].sum())
    return dict(
        toplam_alan=float(a.sum()),
        asagi_bakan=total_down,
        sorunlu_alan=float(a[steep].sum()),
        yatay_tavan=float(a[flat].sum()),
        sorunlu_oran=float(a[steep].sum() / max(a.sum(), 1e-9)),
        en_kotu_egim=float((90.0 - tilt[down]).max()) if down.any() else 0.0,
    )


def steep_faces_bbox(mesh, limit_deg=45.0):
    """Sorunlu yuzlerin nerede toplandigini gosterir."""
    n = mesh.face_normals
    tilt = np.degrees(np.arccos(np.clip(-n[:, 2], -1.0, 1.0)))
    zmin = mesh.bounds[0][2]
    fz = mesh.vertices[mesh.faces][:, :, 2].max(axis=1)
    steep = (n[:, 2] < 0) & (fz > zmin + 0.3) & (tilt < (90.0 - limit_deg))
    if not steep.any():
        return None
    v = mesh.vertices[mesh.faces[steep].reshape(-1)]
    return np.vstack([v.min(axis=0), v.max(axis=0)])
