"""Katı modelleme yardimcilari (trimesh + manifold3d tabanli).

Tum olculer milimetre cinsindendir. Z ekseni her zaman donme eksenidir.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point
from shapely import affinity

SEG = 192          # varsayilan donme cozunurlugu
ENGINE = "manifold"


# --------------------------------------------------------------------------
# temel uretimler
# --------------------------------------------------------------------------
def revolve(profile, segments=SEG):
    """(r, z) kapali poligonunu Z ekseni etrafinda dondurur.

    profile: [(r, z), ...] -- ilk nokta tekrar edilmez, r >= 0.
    """
    prof = np.asarray(profile, dtype=float)
    assert prof.ndim == 2 and prof.shape[1] == 2
    assert (prof[:, 0] >= -1e-9).all(), "r negatif olamaz"
    n = len(prof)
    ang = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=False)
    cos, sin = np.cos(ang), np.sin(ang)

    verts, idx, poles = [], np.zeros((n, segments), dtype=np.int64), {}
    for i, (r, z) in enumerate(prof):
        if r <= 1e-9:                                   # eksen uzerindeki nokta
            key = round(float(z), 9)
            if key not in poles:
                poles[key] = len(verts)
                verts.append((0.0, 0.0, z))
            idx[i, :] = poles[key]
        else:
            base = len(verts)
            verts.extend(zip(r * cos, r * sin, np.full(segments, z)))
            idx[i, :] = np.arange(base, base + segments)

    faces = []
    for i in range(n):
        j = (i + 1) % n
        for k in range(segments):
            m = (k + 1) % segments
            a, b, c, d = idx[i, k], idx[i, m], idx[j, m], idx[j, k]
            if len({a, b, c}) == 3:
                faces.append((a, b, c))
            if len({a, c, d}) == 3:
                faces.append((a, c, d))

    mesh = trimesh.Trimesh(vertices=np.asarray(verts, dtype=float),
                           faces=np.asarray(faces, dtype=np.int64), process=True)
    mesh.fix_normals()
    return mesh


def cyl(r, z0, z1, segments=SEG):
    """Dolu silindir."""
    return revolve([(0, z0), (r, z0), (r, z1), (0, z1)], segments)


def tube(ri, ro, z0, z1, segments=SEG):
    """Ici bos boru."""
    return revolve([(ri, z0), (ro, z0), (ro, z1), (ri, z1)], segments)


def cone(r0, r1, z0, z1, segments=SEG):
    """Dolu koni/kesik koni."""
    return revolve([(0, z0), (r0, z0), (r1, z1), (0, z1)], segments)


def extrude(poly, z0, z1):
    """Shapely poligon(lar)ini Z yonunde katiya cevirir."""
    parts = list(poly.geoms) if hasattr(poly, "geoms") else [poly]
    meshes = []
    for g in parts:
        if g.is_empty or g.area <= 1e-9:
            continue
        m = trimesh.creation.extrude_polygon(g, height=float(z1 - z0))
        m.apply_translation((0, 0, float(z0)))
        meshes.append(m)
    if not meshes:
        raise ValueError("bos poligon")
    return meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)


def sector(r_in, r_out, a0_deg, a1_deg, z0, z1, segments=96):
    """Halka dilimi (bayonet tirnagi, tutus kanali vb.)."""
    a0, a1 = np.radians(a0_deg), np.radians(a1_deg)
    steps = max(4, int(segments * abs(a1 - a0) / (2 * np.pi)) + 2)
    a = np.linspace(a0, a1, steps)
    outer = [(r_out * np.cos(t), r_out * np.sin(t)) for t in a]
    inner = [(r_in * np.cos(t), r_in * np.sin(t)) for t in a[::-1]]
    return extrude(Polygon(outer + inner), z0, z1)


def box(x0, x1, y0, y1, z0, z1):
    return extrude(Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), z0, z1)


def sweep_rings(rings):
    """Sirali kesit halkalarini (her biri (k,3) dizi) kapali bir katiya cevirir.

    Helisel yay gibi supurme govdeler icin. Uc halkalar duz kapakla kapatilir.
    """
    rings = [np.asarray(r, dtype=float) for r in rings]
    k = len(rings[0])
    verts = np.vstack(rings)
    faces = []
    for i in range(len(rings) - 1):
        a, b = i * k, (i + 1) * k
        for j in range(k):
            j2 = (j + 1) % k
            faces.append((a + j, a + j2, b + j2))
            faces.append((a + j, b + j2, b + j))
    for ring_start, flip in ((0, True), ((len(rings) - 1) * k, False)):
        for j in range(1, k - 1):
            tri = (ring_start, ring_start + j, ring_start + j + 1)
            faces.append(tri[::-1] if flip else tri)
    mesh = trimesh.Trimesh(vertices=verts, faces=np.asarray(faces), process=True)
    mesh.fix_normals()
    return mesh


# --------------------------------------------------------------------------
# boolean islemler
# --------------------------------------------------------------------------
def _check(m, tag):
    if len(m.faces) == 0:
        return m                       # bos kesisim: carpisma yok
    if not m.is_volume:
        try:
            m.fix_normals()
            m.fill_holes()
        except Exception:
            pass
    return m


def union(*meshes):
    ms = [m for m in meshes if m is not None]
    return _check(trimesh.boolean.union(ms, engine=ENGINE), "union") if len(ms) > 1 else ms[0]


def diff(a, *cutters):
    cs = [c for c in cutters if c is not None]
    return _check(trimesh.boolean.difference([a] + cs, engine=ENGINE), "diff") if cs else a


def inter(a, b):
    return _check(trimesh.boolean.intersection([a, b], engine=ENGINE), "inter")


def polar(mesh, count, start_deg=0.0):
    """Meshi Z ekseni etrafinda esit acilarla kopyalar."""
    out = []
    for i in range(count):
        m = mesh.copy()
        m.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(start_deg + 360.0 * i / count), (0, 0, 1)))
        out.append(m)
    return out


def rotz(mesh, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), (0, 0, 1)))
    return m


def movez(mesh, dz):
    m = mesh.copy()
    m.apply_translation((0, 0, dz))
    return m


# --------------------------------------------------------------------------
# silindire sarilmis kabartma yazi / cizgi
# --------------------------------------------------------------------------
def text_polygons(s, size_mm, font=None):
    """Yaziyi shapely poligonlarina cevirir (sol-alt kose orijinde).

    Delikler (A, 0, 5 harflerinin ici) ic-ice sayimla bulunur: bir konturun
    icinde bulundugu kontur sayisi tek ise delik, cift ise govdedir.
    """
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family="DejaVu Sans", weight="bold") if font is None else font
    rings = [Polygon(p).buffer(0) for p in TextPath((0, 0), s, size=size_mm, prop=fp)
             .to_polygons(closed_only=True) if len(p) >= 3]
    rings = [r for r in rings if not r.is_empty and r.area > 1e-9]
    out = None
    for i, r in enumerate(rings):
        depth = sum(1 for j, o in enumerate(rings)
                    if j != i and o.contains(r.representative_point()))
        if depth % 2 == 0:
            out = r if out is None else out.union(r)
    for i, r in enumerate(rings):
        depth = sum(1 for j, o in enumerate(rings)
                    if j != i and o.contains(r.representative_point()))
        if depth % 2 == 1 and out is not None:
            out = out.difference(r)
    if out is None or out.is_empty:
        raise ValueError("bos yazi: %r" % s)
    minx, miny, _, _ = out.bounds
    return affinity.translate(out, -minx, -miny)


def wrap_on_cylinder(mesh, radius, z_at, arc_center_deg=0.0, x_center=0.0):
    """XY duzlemindeki duz kabartmayi (X: cevre, Y: radyal, Z: yukseklik)
    yaricapi `radius` olan silindire sarar."""
    v = mesh.vertices.copy()
    theta = np.radians(arc_center_deg) + (v[:, 0] - x_center) / radius
    r = radius + v[:, 1]
    out = mesh.copy()
    out.vertices = np.column_stack([r * np.cos(theta), r * np.sin(theta), v[:, 2] + z_at])
    out.fix_normals()
    return out


def emboss_text(s, size_mm, depth, radius, z_center, arc_center_deg=0.0):
    """Silindir yuzeyine sarilmis kabartma yazi katisi uretir."""
    poly = text_polygons(s, size_mm)
    minx, miny, maxx, maxy = poly.bounds
    flat = extrude(poly, -0.05, depth)                   # Z = kalinlik (radyal olacak)
    flat.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    #   donusum sonrasi: X = cevre, Y = -radyal kalinlik, Z = yazi yuksekligi
    v = flat.vertices.copy()
    v[:, 1] = -v[:, 1]
    v[:, 2] -= (maxy - miny) / 2.0
    flat.vertices = v
    flat.fix_normals()
    return wrap_on_cylinder(flat, radius, z_center, arc_center_deg,
                            x_center=(maxx - minx) / 2.0)


# --------------------------------------------------------------------------
# tutamak / serbest bicimli govdeler
# --------------------------------------------------------------------------
def hull(*meshes):
    """Verilen katilarin disbukey kabugu (sap, kol, gecis parcalari icin)."""
    ms = [m for m in meshes if m is not None]
    return trimesh.util.concatenate(ms).convex_hull if len(ms) > 1 else ms[0].convex_hull


def stadium(x0, y0, x1, y1, r, resolution=24):
    """Iki ucu yuvarlatilmis dikdortgen (kapsul) poligonu -- sap kesiti."""
    from shapely.geometry import LineString
    return LineString([(x0, y0), (x1, y1)]).buffer(r, resolution=resolution)


def loft(sections, cap=True):
    """Sirali (poligon, z) kesitlerini tek bir katiya baglar.

    Tum kesitler ayni kose sayisina yeniden orneklendigi icin poligonlarin
    ayni topolojide (tek halka, deliksiz) olmasi gerekir.
    """
    import numpy as _np
    rings = []
    n = 96
    for poly, z in sections:
        ring = _np.asarray(poly.exterior.coords[:-1], dtype=float)
        # cevre boyunca esit araliklarla yeniden ornekle
        seg = _np.linalg.norm(_np.roll(ring, -1, axis=0) - ring, axis=1)
        s = _np.concatenate([[0.0], _np.cumsum(seg)])
        t = _np.linspace(0.0, s[-1], n, endpoint=False)
        pts = _np.column_stack([_np.interp(t, s, _np.append(ring[:, 0], ring[0, 0])),
                                _np.interp(t, s, _np.append(ring[:, 1], ring[0, 1]))])
        rings.append(_np.column_stack([pts, _np.full(n, float(z))]))
    return sweep_rings(rings) if cap else sweep_rings(rings)


def cross_section_area(poly):
    return float(poly.area)
