"""MINI kepce: 3 parca, pim/O-ring yok, destek yok.

- HAZNE: yuvarlak, Ø38 tabanli, 7 derece konik.  Tabani uc katli bir levha:
  alt deri (1.2) + SURGU KANALI (2.35) + ust deri (1.6).  Iki deride de one
  dogru kaydirilmis Ø21 delik (altta 45 derece havsali: sise agzi ortalanir).
  Kanal, cidarin dibinden gecip sapin icine devam eder; sapin ustunde surgu
  yarigi vardir.  Sap tabanla ayni duzlemde (tablada basilir).
- SURGU (taban plakasi): kanalda kayan DELIKSIZ plaka (onu yuvarlak) + sapin
  icinden gecen kol + sapin ustunden cikan tirtikli basparmak surgusu.
  Kapali: plaka deligin altinda.  Surguyu TRAVEL kadar kendine cek: delik
  acilir, toz asagi.  Plakanin iki yanindaki yay parmaklari kanal duvarindaki
  yuvalara kapali ve acik konumda oturur (klik).
- UST KAPAK: agza klik diye gecen duz kapak (saklama), kulakli.
z = 0 haznenin alt yuzu; ic taban z = FLOOR0 = SLAB_BOT + CH_H + FLOOR_T.
Baski: hazne TABAN TABLADA (agiz yukari), surgu alt yuzu tablada, kapak dis
yuzu tablada.  Tek kopru: kanal tavani (28 mm, haznenin ic tabani).
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g
import scoop_slide as B

P = dict(
    BORE=38.0, DRAFT=7.0, WALL=2.0, FIT=0.3,
    SLAB_BOT=1.2, CH_H=2.35, FLOOR_T=1.6,           # taban levhasi katlari
    HOLE_D=21.0, HOLE_X=-8.5,                        # delik (one dogru)
    PL_HW=14.0, PL_RF=20.5, PL_X1=5.0, PL_T=1.9,     # plaka: yarim genislik, on yaricap, arka kenar, kalinlik
    TRAVEL=24.0,
    STEM_HW=4.0,                                     # kol yarim genisligi (sapin icinden gecer)
    TAB_X0=36.0, TAB_L=6.0, TAB_H=8.5,               # basparmak surgusu (kapali konum x0, uzunluk, ust z)
    FING_L=14.0, FING_T=2.0, FING_SLOT=0.6,          # yay parmagi (plakanin yan kenarinda, arkadan bagli)
    BUMP=0.5, BUMP_W=2.5, BUMP_X=-12.0,              # tumsek (disa), kapali konumdaki x0
    GROOVE_D=0.5, CAP_T=1.6, CAP_SKIRT=4.0, CAP_GROOVE=(3.0, 2.0), SKIRT_T=1.4, EAR_W=6.0, EAR_OUT=4.0,
    HANDLE_L=55.0, HANDLE_W=16.0, HANDLE_H=6.5,
)
SIZES = (15, 30)
cup_depth = B.cup_depth


def _floor0(p=P):
    return p["SLAB_BOT"] + p["CH_H"] + p["FLOOR_T"]


def _r_at(z_in, p=P):
    return p["BORE"] / 2 + z_in * np.tan(np.radians(p["DRAFT"]))


def dims(size, p=P):
    d = cup_depth(size, dict(B.P, BORE=p["BORE"], DRAFT=p["DRAFT"]))
    H = _floor0(p) + d
    return dict(depth=d, H=H, r_rim=_r_at(d, p), r_o_rim=_r_at(d, p) + p["WALL"], r_o_floor=p["BORE"] / 2 + p["WALL"])


def _plate_plan(p, grow=0.0):
    """Plakanin plani: onu r PL_RF yuvarlak, yanlari duz (|y| <= PL_HW), arkasi x = PL_X1."""
    hw, x1 = p["PL_HW"] + grow, p["PL_X1"] + grow
    return Point(0, 0).buffer(p["PL_RF"] + grow, resolution=128).intersection(sbox(-30, -hw, x1, hw)).buffer(0)


def _bumps(p, grow=0.0):
    """Parmak tumsekleri (kapali konum), x'te 45 derece yanakli; grow>0 -> kanal duvarindaki yuva."""
    hw, e, b = p["PL_HW"], grow, p["BUMP"]
    x0, x1 = p["BUMP_X"] - e, p["BUMP_X"] + p["BUMP_W"] + e
    out = []
    for sgn in (1, -1):
        pts = [(x0, hw - 0.3), (x0 + b, hw + b + e), (x1 - b, hw + b + e), (x1, hw - 0.3)]
        out.append(g.extrude(Polygon([(x, sgn * y) for x, y in pts]), p["SLAB_BOT"] - e, p["SLAB_BOT"] + p["PL_T"] + e))
    return out


def _handle(p):
    w, hh = p["HANDLE_W"], p["HANDLE_H"]
    x0 = p["BORE"] / 2 + p["WALL"] - 2.0
    bar = g.box(x0, x0 + p["HANDLE_L"] + 2.0, -w / 2, w / 2, 0.0, hh)
    return g.diff(bar, g.cyl(2.2, -1, hh + 1).apply_translation((x0 + p["HANDLE_L"] - 3.0, 0, 0)))


def build_cup(size, p=P, pockets=True):
    d = dims(size, p)
    H, w = d["H"], p["WALL"]
    rb = p["BORE"] / 2
    f0 = _floor0(p)
    cup = g.revolve([(0, 0), (rb + w, 0), (rb + w, 3.0), (d["r_o_rim"], H), (d["r_rim"], H), (rb, f0), (0, f0)])
    cup = g.union(cup, _handle(p))
    # delikler: ust deri duz, alt deri 45 derece havsali (sise agzi ortalanir)
    z_ch0, z_ch1 = p["SLAB_BOT"], p["SLAB_BOT"] + p["CH_H"]
    rh = p["HOLE_D"] / 2
    cup = g.diff(cup, g.cyl(rh, z_ch0 - 1, f0 + 1).apply_translation((p["HOLE_X"], 0, 0)),
                 g.revolve([(0, -0.1), (rh + p["SLAB_BOT"] + 0.1, -0.1), (rh, p["SLAB_BOT"]), (0, p["SLAB_BOT"])])
                 .apply_translation((p["HOLE_X"], 0, 0)))
    # surgu kanali: plakanin plani (FIT payli) kapali..acik supurmesi + kol yarigi sapin icinde + surgu yarigi ustte
    plan = _plate_plan(p, p["FIT"] / 2).union(sbox(0, -p["PL_HW"] - p["FIT"] / 2, p["PL_X1"] + p["TRAVEL"] + 3.0,
                                                    p["PL_HW"] + p["FIT"] / 2))
    stem = sbox(0, -p["STEM_HW"] - p["FIT"] / 2, p["TAB_X0"] + p["TAB_L"] + p["TRAVEL"] + 3.0, p["STEM_HW"] + p["FIT"] / 2)
    cup = g.diff(cup, g.extrude(plan.union(stem).buffer(0), z_ch0, z_ch1))
    cup = g.diff(cup, g.box(p["TAB_X0"] - p["FIT"] / 2, p["TAB_X0"] + p["TAB_L"] + p["TRAVEL"] + p["FIT"] / 2,
                            -p["STEM_HW"] - p["FIT"] / 2, p["STEM_HW"] + p["FIT"] / 2, z_ch1 - 0.1, p["HANDLE_H"] + 1))
    cup = g.diff(cup, cup_cap_groove(size, p))      # ust kapak klik kanali
    if pockets:                                     # tumsek yuvalari: kapali ve acik
        for dx in (0.0, p["TRAVEL"]):
            cup = g.diff(cup, *[b.apply_translation((dx, 0, 0)) for b in _bumps(p, grow=p["FIT"] / 2)])
    return cup


def build_plate(p=P, opened=False, bumps=True):
    """Surgu: deliksiz plaka + kol + basparmak surgusu."""
    z0 = p["SLAB_BOT"]
    z1 = z0 + p["PL_T"]
    plan = _plate_plan(p)
    hw = p["PL_HW"]
    # yay parmaklari: yan kenar seridi, arkadan bagli, onde serbest (yarik on kenarda acik)
    for sgn in (1, -1):
        ys = hw - p["FING_T"]
        xf = p["PL_X1"] - p["FING_L"]
        plan = plan.difference(sbox(-30, min(sgn * ys, sgn * (ys - p["FING_SLOT"])), xf,
                                    max(sgn * ys, sgn * (ys - p["FING_SLOT"]))))
        plan = plan.difference(sbox(xf - 0.6, min(sgn * (ys - p["FING_SLOT"]), sgn * (hw + 1)), xf,
                                    max(sgn * (ys - p["FING_SLOT"]), sgn * (hw + 1))))  # parmagin serbest ucu
    stem = sbox(p["PL_X1"] - 1.0, -p["STEM_HW"], p["TAB_X0"] + p["TAB_L"], p["STEM_HW"])
    pl = g.extrude(plan.union(stem).buffer(0), z0, z1)
    if bumps:
        pl = g.union(pl, *_bumps(p))
    tab = g.box(p["TAB_X0"], p["TAB_X0"] + p["TAB_L"], -p["STEM_HW"], p["STEM_HW"], z1 - 0.1, p["TAB_H"])
    for k in range(3):                              # tirtik
        xc = p["TAB_X0"] + 1.2 + k * 1.8
        tab = g.diff(tab, g.box(xc - 0.35, xc + 0.35, -p["STEM_HW"] - 1, p["STEM_HW"] + 1, p["TAB_H"] - 0.5, p["TAB_H"] + 1))
    pl = g.union(pl, tab)
    if opened:
        pl.apply_translation((p["TRAVEL"], 0, 0))
    return pl


def build_cap(size, p=P):
    """Ust kapak: agza gecer, etegi kanala klik yapar, kulakli."""
    d = dims(size, p)
    H = d["H"]
    zc0, zc1 = H - p["CAP_GROOVE"][0], H - p["CAP_GROOVE"][1]
    r_w = _r_at(zc1 - _floor0(p), p) + p["WALL"]
    ri = d["r_o_rim"] + p["FIT"] / 2
    ro = ri + p["SKIRT_T"]
    cap = g.union(g.cyl(ro, H, H + p["CAP_T"]), g.tube(ri, ro, H - p["CAP_SKIRT"], H + 0.1))
    lip = g.revolve([(r_w - p["GROOVE_D"] + 0.15, zc0 + 0.15), (r_w - p["GROOVE_D"] + 0.15, zc1 - 0.15),
                     (ri + 0.2, zc1 - 0.15), (ri + 0.2, zc0 + 0.15 - 0.4), (r_w + 0.1, zc0 + 0.15)])
    ear = g.box(ro - 0.5, ro + p["EAR_OUT"], -p["EAR_W"] / 2, p["EAR_W"] / 2, H - 0.6, H + p["CAP_T"])
    return g.union(cap, lip, g.rotz(ear, 180.0))


def cup_cap_groove(size, p=P):
    d = dims(size, p)
    H = d["H"]
    zc0, zc1 = H - p["CAP_GROOVE"][0], H - p["CAP_GROOVE"][1]
    r_w = _r_at(zc1 - _floor0(p), p) + p["WALL"]
    return g.tube(r_w - p["GROOVE_D"], r_w + 3, zc0, zc1)
