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
