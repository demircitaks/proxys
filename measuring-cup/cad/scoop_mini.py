"""MINI kepce: 3 parca, pim/O-ring/ray yok.

- HAZNE: yuvarlak, Ø38 tabanli, 7 derece konik; tabaninda kenara yakin Ø22
  delik (merkez -7 mm, one dogru).  Alt kenarda ve agiz altinda birer klik
  kanali.  Tabandan uzanan kisa sap (tablada basilir).
- TABAN KAPAGI (donen): tabana alttan klik diye gecen 3 mm disk; ayni Ø22 delik
  ve altinda pet sise boynunun girdigi Ø28.3 x 1.6 oturma cukuru (alt yuz duz).
  Kenarindaki kulakla 180 derece cevrilir: delikler ust uste = ACIK, ters =
  KAPALI.  Her iki konumda centik (hazne cidarindaki tumsekler kapagin
  etegindeki yuvalara oturur).
- UST KAPAK: agza klik diye gecen duz kapak (saklama), kulakli.
z = 0 haznenin alt yuzu (taban kapaginin oturdugu duzlem); ic taban z = FLOOR_T.
Baski: hazne AGIZ YUKARI (taban tablada), kapaklar duz (dis yuz tablada).
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g
import scoop_slide as B

P = dict(
    BORE=38.0, DRAFT=7.0, WALL=2.0, FLOOR_T=1.6, FIT=0.3,
    HOLE_D=22.0, HOLE_X=-7.0,          # taban deligi (one dogru kaydirilmis)
    SEAT_ID=28.3, SEAT_H=1.6,               # sise boynu oturma cukuru (plakanin altinda, PCO-1881 dis Ø27.4)
    SHUT_T=3.0, SKIRT_T=1.4, SKIRT_H=2.6,   # taban kapagi: plaka (alti dumduz), etek
    GROOVE_D=0.5, GROOVE_Z=(1.3, 2.3),      # alt klik kanali (cidarda)
    LIP=0.4,                                # etek dudagi
    DET=0.35, DET_W=2.0,                    # centik tumsegi (cidarda, +-90 derecede)
    EAR_W=6.0, EAR_OUT=4.0,                 # kapak kulagi
    CAP_T=1.6, CAP_SKIRT=4.0, CAP_GROOVE=(3.0, 2.0),  # ust kapak: kalinlik, etek boyu, kanal (agizdan asagi z0,z1)
    HANDLE_L=55.0, HANDLE_W=10.0, HANDLE_H=6.0, GUSSET_TOP=8.5,
)
SIZES = (15, 30)
cup_depth = B.cup_depth


def _r_at(z_in, p=P):
    """Ic yaricap, ic tabandan z_in yukarida."""
    return p["BORE"] / 2 + z_in * np.tan(np.radians(p["DRAFT"]))


def dims(size, p=P):
    d = cup_depth(size, dict(B.P, BORE=p["BORE"], DRAFT=p["DRAFT"]))
    H = p["FLOOR_T"] + d
    return dict(depth=d, H=H, r_rim=_r_at(d, p), r_o_rim=_r_at(d, p) + p["WALL"], r_o_floor=p["BORE"] / 2 + p["WALL"])


def _handle(size, p):
    """Tabandan uzanan sap: cubuk tablada (z 0..HANDLE_H), cidara 45 derece pahli
    kosebentle baglanir (taban kapaginin etegi altindan gecer)."""
    w, hh = p["HANDLE_W"], p["HANDLE_H"]
    r_sk = p["BORE"] / 2 + p["WALL"] + p["FIT"] / 2 + p["SKIRT_T"]     # etek dis yaricapi
    x0 = r_sk + 0.5
    bar = g.extrude(Polygon([(x0, -w / 2), (x0 + p["HANDLE_L"], -w / 2), (x0 + p["HANDLE_L"], w / 2), (x0, w / 2)])
                    .buffer(0), 0.0, hh)
    bar = g.diff(bar, g.cyl(2.2, -1, hh + 1).apply_translation((x0 + p["HANDLE_L"] - 5.0, 0, 0)))   # asma deligi
    # kosebent (x,z): cidarin icinden baslar, altta 45 derece pah
    zt = p["GUSSET_TOP"]
    prof = Polygon([(p["BORE"] / 2 + 0.5, p["SKIRT_H"] + 0.4 + (x0 - p["BORE"] / 2 - 0.5)), (p["BORE"] / 2 + 0.5, zt),
                    (x0 + 6.0, zt), (x0 + 6.0, 0.0), (x0, 0.0), (x0, p["SKIRT_H"] + 0.4)])
    gus = g.extrude(prof, -w / 2, w / 2)
    gus.apply_transform(np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))  # (x,z,y)->(x,y,z)
    gus.apply_transform(np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], float)) # yon duzelt
    gus.fix_normals()
    return g.union(bar, gus)


def build_cup(size, p=P, bumps=True):
    d = dims(size, p)
    H, w = d["H"], p["WALL"]
    rb = p["BORE"] / 2
    zs = p["SKIRT_H"] + 0.4                       # etek bolgesinde dis cidar dik
    cup = g.revolve([(0, 0), (rb + w, 0), (rb + w, zs), (d["r_o_rim"], H), (d["r_rim"], H), (rb, p["FLOOR_T"]),
                     (0, p["FLOOR_T"])])
    cup = g.union(cup, _handle(size, p))
    # taban deligi
    cup = g.diff(cup, g.cyl(p["HOLE_D"] / 2, -1, p["FLOOR_T"] + 1).apply_translation((p["HOLE_X"], 0, 0)))
    # alt klik kanali (etek dudagi buraya oturur) ve ust klik kanali (ust kapak)
    z0, z1 = p["GROOVE_Z"]
    cup = g.diff(cup, g.tube(rb + w - p["GROOVE_D"], rb + w + 2, z0, z1))
    zc0, zc1 = H - p["CAP_GROOVE"][0], H - p["CAP_GROOVE"][1]
    r_w = _r_at(zc1 - p["FLOOR_T"], p) + w
    cup = g.diff(cup, g.tube(r_w - p["GROOVE_D"], r_w + 3, zc0, zc1))
    if bumps:                                   # centik tumsekleri (+-90), etegin ic yuzune
        for a in (90.0, 270.0):
            b = g.box(rb + w - 0.2, rb + w + p["DET"], -p["DET_W"] / 2, p["DET_W"] / 2, 0.15, z0 - 0.15)
            cup = g.union(cup, g.rotz(b, a))
    return cup


def build_shutter(p=P, opened=True, notches=True):
    """Donen taban kapagi.  opened=True: delik haznenin deligiyle ust uste (kulak +90)."""
    rb = p["BORE"] / 2
    ri = rb + p["WALL"] + p["FIT"] / 2                 # etek ic yaricapi (cidara oturur)
    ro = ri + p["SKIRT_T"]
    t = p["SHUT_T"]
    plate = g.cyl(ro, -t, 0.0)
    skirt = g.tube(ri, ro, -0.1, p["SKIRT_H"])
    z0, z1 = p["GROOVE_Z"]
    lip = g.revolve([(ri - p["LIP"], z0 + 0.15 + p["LIP"]), (ri, z0 + 0.15), (ri + 0.2, z0 + 0.15),
                     (ri + 0.2, z1 - 0.15), (ri, z1 - 0.15)])           # kanala giren dudak, alti pahli
    ear = g.box(ro - 0.5, ro + p["EAR_OUT"], -p["EAR_W"] / 2, p["EAR_W"] / 2, -t, p["SKIRT_H"])
    sh = g.union(plate, skirt, lip, g.rotz(ear, 90.0))
    # delik + alttan oturma cukuru
    sh = g.diff(sh, g.cyl(p["HOLE_D"] / 2, -t - 1, 1).apply_translation((p["HOLE_X"], 0, 0)),
                g.cyl(p["SEAT_ID"] / 2, -t - 1, -t + p["SEAT_H"]).apply_translation((p["HOLE_X"], 0, 0)))
    if notches:                                  # tumsek yuvalari (kulak acisinda ve karsisinda)
        for a in (90.0, 270.0):
            n = g.box(ri - 0.2, ri + p["DET"] + p["FIT"] / 2, -p["DET_W"] / 2 - p["FIT"] / 2, p["DET_W"] / 2 + p["FIT"] / 2,
                      0.0, z0)
            sh = g.diff(sh, g.rotz(n, a))
    if not opened:
        sh = g.rotz(sh, 180.0)
    return sh


def build_cap(size, p=P):
    """Ust kapak: agza gecer, etegi kanala klik yapar, kulakli."""
    d = dims(size, p)
    H = d["H"]
    zc0, zc1 = H - p["CAP_GROOVE"][0], H - p["CAP_GROOVE"][1]
    r_w = _r_at(zc1 - p["FLOOR_T"], p) + p["WALL"]
    ri = d["r_o_rim"] + p["FIT"] / 2
    ro = ri + p["SKIRT_T"]
    cap = g.union(g.cyl(ro, H, H + p["CAP_T"]), g.tube(ri, ro, H - p["CAP_SKIRT"], H + 0.1))
    lip = g.revolve([(r_w - p["GROOVE_D"] + 0.15, zc0 + 0.15), (r_w - p["GROOVE_D"] + 0.15, zc1 - 0.15),
                     (ri + 0.2, zc1 - 0.15), (ri + 0.2, zc0 + 0.15 - 0.4), (r_w + 0.1, zc0 + 0.15)])   # ustu pahli
    ear = g.box(ro - 0.5, ro + p["EAR_OUT"], -p["EAR_W"] / 2, p["EAR_W"] / 2, H - 0.6, H + p["CAP_T"])
    return g.union(cap, lip, g.rotz(ear, 180.0))
