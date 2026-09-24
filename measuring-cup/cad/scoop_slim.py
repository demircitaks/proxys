"""SADE surmeli kepce: altta ve ustte surmeli kapak, centikli tutucu, ince sap.

Ust kapak ayni zamanda SILME kenaridir: kapatirken on kenari fazla tozu
super; doz, kapagin altinda kalan hacimdir.  Alt plaka tabandir; O-ring
uzerine kama ile sikisir.  Her iki kapak da sapa dogru kayar ve kapali
konumda bir centige oturur (cantada acilmasin).

z = 0: alt plakanin ust yuzu (taban).  z = h: ust kapagin alt yuzu (agiz).
Baski yonu: hazne AGIZ YUKARI (kanal dudaklari tablada); kapaklar duz.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g
import scoop_slide as B   # alt kanal, O-ring, huni ayni

P = dict(B.P)
P.update(dict(
    TRAVEL      = 34.0,
    # --- ust kapak raylari (agiz hizasinda, disarida iki C ray) ----------
    TOP_RAIL_T  = 2.2,    # ray duvar kalinligi (radyal)
    TOP_LIP     = 1.8,    # kapagin ustune binen dudak
    LID_T       = 2.0,
    LID_LEN_BACK= 12.0,   # kapagin kabin arkasina tasan kismi (kapaliyken)
    TAB_H       = 4.0,    # parmak tirnagi
    # --- centik ------------------------------------------------------------
    DET_R       = 0.45,   # tumsek yuksekligi
    DET_LEN     = 3.0,
    # --- sap: tek parca altigen cubuk ------------------------------------
    HANDLE_L    = 88.0,
    HANDLE_W    = 12.0,
    HANDLE_H    = 8.0,
    HANDLE_Z0   = 1.0,    # alt plakanin (z<0) ustunde, ust kapagin altinda
))
SIZES = B.SIZES
cup_depth, _r_at, brim_volume, report = B.cup_depth, B._r_at, B.brim_volume, B.report


def _rim_geo(size, p=P):
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]                # agizda dis yaricap
    y_in = r_o + p["FIT"] / 2                    # ray ic yuzu = kapak kenari
    return h, r_o, y_in


# ===========================================================================
# HAZNE
# ===========================================================================
def _top_rails(size, p=P):
    """Ust kapagin iki kenarini tasiyan C raylar; on ve arka aciktir."""
    h, r_o, y_in = _rim_geo(size, p)
    y_out = y_in + p["TOP_RAIL_T"]
    z_led = h - 1.4                              # kapagin oturdugu cikinti
    x0, x1 = -r_o - 1.0, r_o + 1.0
    parts = []
    for s in (1, -1):
        lo, hi = sorted((s * y_in, s * y_out))
        parts.append(g.extrude(sbox(x0, lo, x1, hi), z_led, h + p["LID_T"] + p["FIT"] + 1.2))
        # alt cikinti: kapagin alt yuzu tam agiz duzleminde (z = h) durur
        lo2, hi2 = sorted((s * (y_in - p["TOP_LIP"]), s * y_out))
        parts.append(g.extrude(sbox(x0, lo2, x1, hi2), z_led, h))
        # ust dudak
        parts.append(g.extrude(sbox(x0, lo2, x1, hi2), h + p["LID_T"] + p["FIT"],
                               h + p["LID_T"] + p["FIT"] + 1.2))
        # centik tumsegi: kapali konumda kapagin centigine oturur (on tarafta)
        parts.append(g.extrude(sbox(-r_o + 6.0, min(s * (y_in + 0.3), s * (y_in - p["DET_R"])),
                                    -r_o + 6.0 + p["DET_LEN"], max(s * (y_in + 0.3), s * (y_in - p["DET_R"]))),
                               h + 0.2, h + p["LID_T"] - 0.2))
    return parts


def _handle(size, p=P):
    """Altigen kesitli ince cubuk: alt ve ust yuzleri 45 derece pahli, boylece
    hazneyle birlikte agiz yukari basilirken destek istemez."""
    w, hh = p["HANDLE_W"], p["HANDLE_H"]
    z0 = p["HANDLE_Z0"]
    c = hh / 2 - 1.0                             # pah boyu (dikey 1 mm kalir)
    hexa = Polygon([(-w / 2 + c, 0), (w / 2 - c, 0), (w / 2, c), (w / 2, hh - c),
                    (w / 2 - c, hh), (-w / 2 + c, hh), (-w / 2, hh - c), (-w / 2, c)])
    bar = g.extrude(hexa, 0.0, p["HANDLE_L"] + 20.0)      # z boyunca uzat, sonra x'e cevir
    bar.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    bar.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    # simdi bar: x 0..L+20, kesit (y,z) hexagon; z'yi z0'a tasi
    bar.apply_translation((18.0, 0.0, z0))
    bar = g.diff(bar, g.cyl(2.2, -5, 20).apply_translation((p["HANDLE_L"] + 12.0, 0, 0)))  # asma deligi
    bar = g.inter(bar, g.box(0, p["HANDLE_L"] + 18.0, -10, 10, -10, 30))
    return bar


def build_body(size, p=P, strut=True):
    """strut=True: sapin altina kirilip atilan baski payandasi eklenir
    (yalniz STL icin; dogrulama payandasiz yapilir, montajda zaten olmaz)."""
    h = cup_depth(size, p)
    prof = [
        (p["BORE"] / 2, 0.0), (_r_at(h, p), h), (_r_at(h, p) + p["WALL"], h),
        (p["FLANGE_R"], p["FLANGE_T"] + (p["FLANGE_R"] - p["BORE"] / 2 - p["WALL"])),  # 45 derece
        (p["FLANGE_R"], 1.7), (p["FLANGE_R"] - 0.5, 1.2), (p["FLANGE_R"], 0.7),   # huni klik yuvasi
        (p["FLANGE_R"], 0.0),
    ]
    body = g.revolve(prof)
    grooves = g.inter(g.union(*B._grooves(p)), g.cyl(p["FLANGE_R"] + 0.01, -10, 1))
    body = g.union(body, grooves, *_top_rails(size, p), _handle(size, p))
    # alt plakanin ciktigi arka acikligi
    zl = -(p["PLATE_T"] + p["FIT"] + p["LIP_T"])
    body = g.diff(body, g.extrude(sbox(12.0, -(p["PLATE_HW"] + p["FIT"] / 2), 60.0, p["PLATE_HW"] + p["FIT"] / 2),
                                  zl - 0.1, zl + p["LIP_T"] + 0.05))
    # alt plaka centik tumsegi (kanal ic duvarinda, onde)
    y_in = p["PLATE_HW"] + p["FIT"] / 2
    for s in (1, -1):
        body = g.union(body, g.extrude(sbox(-10.0, min(s * (y_in + 0.3), s * (y_in - p["DET_R"])),
                                            -10.0 + p["DET_LEN"], max(s * (y_in + 0.3), s * (y_in - p["DET_R"]))),
                                       -p["PLATE_T"] + 0.2, -0.2))
    # O-ring yuvasi
    body = g.diff(body, g.tube(p["ORING_R"] - p["ORING_GW"] / 2, p["ORING_R"] + p["ORING_GW"] / 2, -0.1, p["ORING_GD"]))
    # hazne bosluğu en sonda
    top = h + 10.0
    body = g.diff(body, g.revolve([(0, -0.2), (p["BORE"] / 2, -0.2), (p["BORE"] / 2, 0), (_r_at(h, p), h),
                                   (_r_at(top, p), top), (0, top)]))
    # --- kirilip atilan baski payandasi: sap tabladan 3.5 mm yukarida basliyor --
    # 0.8 mm'lik ince duvar, ustunde 0.25 mm bosluk; baskidan sonra elle kirilir.
    zl = -(p["PLATE_T"] + p["FIT"] + p["LIP_T"])
    # boolean cakisik yuzey artiklarini at (gozenek kenarinda kil gibi halka olusabiliyor)
    parts = body.split(only_watertight=False)
    body = max(parts, key=lambda m: abs(m.volume))
    if not strut:
        return body
    strut_ = g.union(g.box(27.0, p["HANDLE_L"] + 14.0, -0.4, 0.4, zl, p["HANDLE_Z0"] - 0.25),
                     g.box(27.0, p["HANDLE_L"] + 14.0, -2.0, 2.0, zl, zl + 0.6))
    return trimesh.util.concatenate([body, strut_])


# ===========================================================================
# ALT PLAKA (uzengisiz; arkada asagi donuk parmak tirnagi + centik)
# ===========================================================================
def plate_plan(p=P):
    return B.slider_plan(p)


def build_plate(p=P, opened=False):
    plate = g.extrude(plate_plan(p), -p["PLATE_T"], 0.0)
    xb = p["PLATE_BACK"]
    tab = g.extrude(sbox(xb - 3.0, -p["PLATE_HW"] + 4, xb, p["PLATE_HW"] - 4), -p["PLATE_T"] - p["TAB_H"], -p["PLATE_T"])
    tab = g.hull(tab, g.extrude(sbox(xb - 3.0 - p["TAB_H"], -p["PLATE_HW"] + 4, xb, p["PLATE_HW"] - 4), -p["PLATE_T"] - 0.1, -p["PLATE_T"]))
    plate = g.union(plate, tab)
    # centik: kenarda tumsege oturan oyuk (kapali konumda tumsek x=-17..-14'te)
    for s in (1, -1):
        plate = g.diff(plate, g.extrude(sbox(-10.4, min(s * (p["PLATE_HW"] + 1), s * (p["PLATE_HW"] - p["DET_R"] - 0.1)),
                                             -9.6 + p["DET_LEN"], max(s * (p["PLATE_HW"] + 1), s * (p["PLATE_HW"] - p["DET_R"] - 0.1))),
                                        -p["PLATE_T"] - 1, 1))
    if opened:
        plate = plate.copy(); plate.apply_translation((p["TRAVEL"], 0, 0))
    return plate


# ===========================================================================
# UST KAPAK (silme kenari; arkada yukari donuk tirnak + centik)
# ===========================================================================
def build_lid(size, p=P, opened=False):
    h, r_o, y_in = _rim_geo(size, p)
    hw = y_in - p["FIT"] / 2                       # kapak yari genisligi (= r_o)
    circ = Point(0, 0).buffer(hw, resolution=96)
    plan = circ.intersection(sbox(-hw - 1, -hw, 0, hw)).union(sbox(0, -hw, r_o + p["LID_LEN_BACK"], hw)).buffer(0)
    lid = g.extrude(plan, h, h + p["LID_T"])
    xb = r_o + p["LID_LEN_BACK"]
    tab = g.extrude(sbox(xb - 3.0, -hw + 5, xb, hw - 5), h + p["LID_T"], h + p["LID_T"] + p["TAB_H"])
    tab = g.hull(tab, g.extrude(sbox(xb - 3.0 - p["TAB_H"], -hw + 5, xb, hw - 5), h + p["LID_T"], h + p["LID_T"] + 0.1))
    lid = g.union(lid, tab)
    for s in (1, -1):
        lid = g.diff(lid, g.extrude(sbox(-r_o + 5.6, min(s * (hw + 1), s * (hw - p["DET_R"] - 0.1)),
                                         -r_o + 6.4 + p["DET_LEN"], max(s * (hw + 1), s * (hw - p["DET_R"] - 0.1))),
                                    h - 1, h + p["LID_T"] + 1))
    if opened:
        lid = lid.copy(); lid.apply_translation((2 * r_o + 4.0, 0, 0))
    return lid


def lid_travel(size, p=P):
    return 2 * _rim_geo(size, p)[1] + 4.0


build_funnel = B.build_funnel
build_gasket = B.build_gasket
open_fraction = B.open_fraction
