"""MINI kepce: 3 parca, pim/O-ring yok, destek yok.

- HAZNE: yuvarlak, ust kismi 7 derece konik, altta 45 derecelik HUNI; en altta
  Ø22 aciklik = tabanin tamami (duz taban yok).  Aciklik, haznenin altindaki
  ince TABAN LEVHASININ (alt deri + surgu kanali + ust deri) icinden gecer.
  Dis yuz altta 45 derece pahli (hafif huni).  Acikligin altinda 45 derece
  koniyle daralan Ø20.6 BORU: 500 mL pet su sisesinin boynuna 8 mm girer
  (disari dokulmez).  SAP AGIZ HIZASINDA, cidara bagli; kokunde catal yarigi.
- SURGU (taban plakasi): kanalda kayan DELIKSIZ plaka + arkaya uzanan kol +
  haznenin disinda dik yukselen AYAK + sapin ustunde tirtikli basparmak
  surgusu.  Kapali: plaka acikligin altinda, yay parmaklari kanal duvarindaki
  yuvaya oturur (klik).  Surguyu TRAVEL kadar kendine cek: aciklik tamamen
  acilir; ayak catalin sonuna dayanir.  Ayak boyu hazneye gore (15/30).
- UST KAPAK: agza klik diye gecen duz kapak; etegi sap hizasinda kesik.
z = 0 haznenin alt yuzu; aciklik z = FLOOR0; agiz z = H.
Baski: hazne AGIZ TABLADA (ters; sap tablada, huni yukari), surgu plaka
tablada ayak dik, kapak dis yuzu tablada.  Kopru: kanal tavani (26 mm).
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g
import scoop_slide as B

P = dict(
    BORE=38.0, DRAFT=7.0, WALL=2.0, FIT=0.3,
    SLAB_BOT=1.8, CH_H=2.3, FLOOR_T=1.6,            # taban levhasi katlari (alt deri, kanal, ust deri)
    HOLE_D=22.0,                                     # en alttaki aciklik (merkezde) = tabanin tamami
    SPOUT_OD=20.6, SPOUT_WALL=1.1, SPOUT_L=8.0,      # sise boynuna GIREN boru (PCO-1881 ic Ø21.74, 26/22 ~21.4)
    FUN_A=45.0, FUN_R1=19.0,                         # huni: aciklik yaricapindan FUN_R1'e 45 derece, sonra 7 derece cidar
    BASE_R=17.5,                                     # taban levhasi yaricapi (haznenin altindaki daire)
    PL_HW=13.0, PL_RF=17.0, PL_X1=11.0, PL_T=2.0,    # plaka: yarim genislik, on yaricap, arka kenar, kalinlik
    TRAVEL=29.0,
    STEM_HW=4.0,                                     # kol / ayak yarim genisligi (catal yarigindan gecer)
    LEG_T=6.0, LEG_GAP=2.2,                          # ayak kalinligi (x), ayagin cidardan/kapak eteginden uzakligi
    TAB_H=3.5,                                       # basparmak surgusunun sap ustunden yuksekligi
    FING_L=14.0, FING_T=2.0, FING_SLOT=0.6,          # yay parmagi (plakanin yan kenarinda, arkadan bagli)
    BUMP=0.5, BUMP_W=2.5, BUMP_X=-3.0,               # tumsek (disa), kapali konumdaki x0
    GROOVE_D=0.5, CAP_T=1.6, CAP_SKIRT=4.0, CAP_GROOVE=(3.0, 2.0), SKIRT_T=1.4, EAR_W=6.0, EAR_OUT=4.0,
    HANDLE_L=58.0, HANDLE_W=16.0, HANDLE_H=6.5,      # sap: agiz hizasinda (z H-HANDLE_H .. H)
)
SIZES = (15, 30)
cup_depth = B.cup_depth


def _floor0(p=P):
    return p["SLAB_BOT"] + p["CH_H"] + p["FLOOR_T"]


def _fun_h(p=P):
    return (p["FUN_R1"] - p["HOLE_D"] / 2) / np.tan(np.radians(p["FUN_A"]))


def _fun_vol(p=P):
    r0, r1, h = p["HOLE_D"] / 2, p["FUN_R1"], _fun_h(p)
    return np.pi * h / 3 * (r0 * r0 + r0 * r1 + r1 * r1)


def _r_at(z_in, p=P):
    """Ic yaricap, huni agzindan (aciklik) z_in yukarida."""
    h = _fun_h(p)
    if z_in <= h:
        return p["HOLE_D"] / 2 + z_in * np.tan(np.radians(p["FUN_A"]))
    return p["FUN_R1"] + (z_in - h) * np.tan(np.radians(p["DRAFT"]))


def dims(size, p=P):
    """Derinlik: huni + 7 derecelik kisim = size mL (silme)."""
    pb = dict(B.P, BORE=2 * p["FUN_R1"], DRAFT=p["DRAFT"])
    v_up = size * 1000.0 - _fun_vol(p)
    lo, hi = 0.1, 200.0
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if B.brim_volume(m, pb) < v_up else (lo, m)
    d = _fun_h(p) + (lo + hi) / 2
    H = _floor0(p) + d
    return dict(depth=d, H=H, r_rim=_r_at(d, p), r_o_rim=_r_at(d, p) + p["WALL"], fun_h=_fun_h(p))


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


def _leg_x0(size, p):
    return dims(size, p)["r_o_rim"] + p["LEG_GAP"]


def _handle(size, p):
    """Sap agiz hizasinda; kokunde catal yarigi (ayak + TRAVEL)."""
    d = dims(size, p)
    H, w, hh = d["H"], p["HANDLE_W"], p["HANDLE_H"]
    x0 = d["r_o_rim"] - 1.5
    bar = g.box(x0, x0 + p["HANDLE_L"], -w / 2, w / 2, H - hh, H)
    bar = g.diff(bar, g.cyl(2.2, H - hh - 1, H + 1).apply_translation((x0 + p["HANDLE_L"] - 4.0, 0, 0)))
    lx = _leg_x0(size, p)
    fork = g.box(lx - p["FIT"] / 2, lx + p["LEG_T"] + p["TRAVEL"] + p["FIT"] / 2, -p["STEM_HW"] - p["FIT"] / 2,
                 p["STEM_HW"] + p["FIT"] / 2, H - hh - 1, H + 1)
    return g.diff(bar, fork)


def build_cup(size, p=P, pockets=True):
    d = dims(size, p)
    H, w = d["H"], p["WALL"]
    f0 = _floor0(p)
    rh, r1, fh = p["HOLE_D"] / 2, p["FUN_R1"], d["fun_h"]
    rb = p["BASE_R"]
    # dis: taban levhasi yaricapi rb'den 45 derece pahla cidara, sonra 7 derece; ic: huni + cidar
    z_ch = f0 + (r1 + w - rb)                        # pahin cidara ulastigi z
    outer = [(0, 0), (rb, 0), (rb, f0), (r1 + w, z_ch), (d["r_o_rim"], H)]
    inner = [(d["r_rim"], H), (r1, f0 + fh), (rh, f0), (0, f0)]
    cup = g.revolve(outer + inner)
    base = g.cyl(rb, 0.0, f0)
    cup = g.union(cup, base, _handle(size, p))
    # aciklik levhanin icinden asagi; alt deride 45 derece koni -> sise boynuna giren boru
    z_ch0, z_ch1 = p["SLAB_BOT"], p["SLAB_BOT"] + p["CH_H"]
    r_so = p["SPOUT_OD"] / 2
    r_si = r_so - p["SPOUT_WALL"]
    cup = g.union(cup, g.tube(r_si, r_so, -p["SPOUT_L"], 0.2))
    cup = g.diff(cup, g.cyl(rh, z_ch0 - 0.01, f0 + 0.5), g.cyl(r_si, -p["SPOUT_L"] - 1, z_ch0),
                 g.revolve([(0, z_ch0 - (rh - r_si) - 0.01), (r_si, z_ch0 - (rh - r_si) - 0.01), (rh + 0.01, z_ch0 + 0.01),
                            (0, z_ch0 + 0.01)]))
    # surgu kanali: plakanin plani (FIT payli) kapali..acik supurmesi + kol yarigi + surgu yarigi ustte
    plan = _plate_plan(p, p["FIT"] / 2).union(sbox(0, -p["PL_HW"] - p["FIT"] / 2, rb + 5.0, p["PL_HW"] + p["FIT"] / 2))
    cup = g.diff(cup, g.extrude(plan.buffer(0), z_ch0, z_ch1))
    cup = g.diff(cup, cup_cap_groove(size, p))      # ust kapak klik kanali
    if pockets:                                     # tumsek yuvasi: yalniz kapali konum (acik konumu ayak catalda durur)
        cup = g.diff(cup, *_bumps(p, grow=p["FIT"] / 2))
    return cup


def build_plate(size, p=P, opened=False, bumps=True):
    """Surgu: deliksiz plaka + kol + dik ayak + basparmak surgusu (boy hazneye gore)."""
    d = dims(size, p)
    H = d["H"]
    z0 = p["SLAB_BOT"]
    z1 = z0 + p["PL_T"]
    plan = _plate_plan(p)
    hw = p["PL_HW"]
    for sgn in (1, -1):                              # yay parmaklari: yan kenar seridi, arkadan bagli, onde serbest
        ys = hw - p["FING_T"]
        xf = p["PL_X1"] - p["FING_L"]
        plan = plan.difference(sbox(-30, min(sgn * ys, sgn * (ys - p["FING_SLOT"])), xf,
                                    max(sgn * ys, sgn * (ys - p["FING_SLOT"]))))
        plan = plan.difference(sbox(xf - 0.6, min(sgn * (ys - p["FING_SLOT"]), sgn * (hw + 1)), xf,
                                    max(sgn * (ys - p["FING_SLOT"]), sgn * (hw + 1))))
    lx = _leg_x0(size, p)
    stem = sbox(p["PL_X1"] - 1.0, -p["STEM_HW"], lx + p["LEG_T"], p["STEM_HW"])
    pl = g.extrude(plan.union(stem).buffer(0), z0, z1)
    if bumps:
        pl = g.union(pl, *_bumps(p))
    leg = g.box(lx, lx + p["LEG_T"], -p["STEM_HW"], p["STEM_HW"], z1 - 0.1, H + p["TAB_H"])
    for k in range(3):                               # tirtik
        xc = lx + 1.2 + k * 1.8
        leg = g.diff(leg, g.box(xc - 0.35, xc + 0.35, -p["STEM_HW"] - 1, p["STEM_HW"] + 1, H + p["TAB_H"] - 0.5, H + p["TAB_H"] + 1))
    pl = g.union(pl, leg)
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
    cap = g.union(cap, lip, g.rotz(ear, 180.0))
    # etek sap hizasinda kesik (sap agiz hizasinda cidara bagli)
    gap = g.box(0, ro + 2, -p["HANDLE_W"] / 2 - p["FIT"], p["HANDLE_W"] / 2 + p["FIT"], H - p["CAP_SKIRT"] - 1, H + 0.02)
    return g.diff(cap, gap)


def cup_cap_groove(size, p=P):
    d = dims(size, p)
    H = d["H"]
    zc0, zc1 = H - p["CAP_GROOVE"][0], H - p["CAP_GROOVE"][1]
    r_w = _r_at(zc1 - _floor0(p), p) + p["WALL"]
    return g.tube(r_w - p["GROOVE_D"], r_w + 3, zc0, zc1)
