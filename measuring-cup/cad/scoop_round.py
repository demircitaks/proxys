"""YUVARLAK kepce: alt ve ust kapak birer disk, sap kokundeki tek dikey mil
etrafinda yana DONER.  Ray, kanal, kizak yok; silüet bastan sona yuvarlak.

- Ust kapak (disk) kapatilirken on kenari fazla tozu super -> silme.
- Alt disk tabandir; iki on tirnagi flansin kenarina klik yapar ve diski
  O-ring'e ceker.  Acmak icin diski sapin altina dogru cevirirsiniz.
- Ikisi de ayni mile takilir; mil alttan surulur, ustte tirnakla tutunur.
- Haznenin alti hafif HUNI: 45 derecelik koni, ucu PCO-1881 pet sise
  agzina giren Ø20.8 boru.  Alt disk huninin ustundeki yariktan yana kayar;
  huni govdeye +y tarafindaki kanatla baglidir (diskin supurmedigi taraf).
z = 0 alt diskin ust yuzu (taban); z = h ust diskin alt yuzu (agiz).
Baski: hazne AGIZ TABLADA (ters), huni yukari; koni her iki yonde 45 derece.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g
import scoop_slide as B

P = dict(B.P)
P.update(dict(
    FLANGE_R    = 24.0,
    FLANGE_T    = 2.4,
    DISC_T      = 2.5,
    PIVOT_X     = 28.5,   # mil ekseni (flansin 4.5 mm disinda, sap kokunde)
    PIN_D       = 4.0,
    BOSS_R      = 5.2,    # mil etrafindaki gobek
    EAR_R       = 6.2,    # disklerin mile uzanan kulagi
    OPEN_DEG    = 150.0,  # diskin acik konumu (sapin uzerine / altina)
    # ust kapak tutucu boncugu (dis cidarda, agzin altinda)
    LID_BEAD    = 0.9,
    LID_BEAD_Z  = 3.2,
    # teget kilit: diskin on kenarindaki tirnak, kapanirken yandan bir tunele girer;
    # tunel tavani 0.45 mm alcalir (disk O-ring'e sikisir), sonunda kucuk bir
    # tumsek vardir (O-ring yay gorevi gorur -> centik)
    TAB_ANG     = 0.0,    # tirnak acisi (on = 180 dereceye gore)
    TAB_W       = 14.0,   # tirnak genisligi (mm, teget yonde)
    TAB_H       = 2.0,    # tirnak yuksekligi (disk yuzeyinden)
    TAB_R       = 1.6,    # tirnak radyal kalinligi (disk kenarindan iceri)
    LOCK_DEG    = 14.0,   # tunelin acisal uzunlugu (kapanmanin son 14 derecesi)
    LOCK_WEDGE  = 0.45,
    DET_R       = 0.35,
    # sap
    HANDLE_L    = 86.0,
    HANDLE_W    = 12.0,
    HANDLE_H    = 8.0,
    # sapin ust yuzu agiz duzlemindedir (z = h): ters baskida tablaya oturur,
    # ust disk uzerinden kayar; alt diskin kulagi altindan gecer.
    # huni (govdenin alti)
    FUN_GAP     = 0.6,    # alt diskin alti ile huni ust halkasi arasi
    FUN_TOP_RO  = 24.6,   # huni ust halkasi dis yaricap (flans + kilit yuvasi ile ayni)
    FUN_WALL    = 1.4,
    SPOUT_D     = 20.8,   # PCO-1881 ic capi 21.74 -> 0.47 mm/yan bosluk
    SPOUT_L     = 7.0,    # boynun icine giren duz kisim
    FIN_A0      = 35.0,   # baglanti kanadi (+y tarafi), acisal araligi
    FIN_A1      = 145.0,
    FIN_RO      = 26.5,
))
SIZES = B.SIZES
cup_depth, _r_at, brim_volume, report = B.cup_depth, B._r_at, B.brim_volume, B.report


def pivot_axis(p=P):
    return [p["PIVOT_X"], 0.0, 0.0], [0.0, 0.0, 1.0]


def _disc_plan(r_disc, p=P):
    """Disk + mile uzanan kulak (tek parca plan)."""
    disc = Point(0, 0).buffer(r_disc, resolution=128)
    ear = Point(p["PIVOT_X"], 0).buffer(p["EAR_R"], resolution=48)
    bridge = sbox(r_disc - 6.0, -p["EAR_R"], p["PIVOT_X"], p["EAR_R"])
    return disc.union(ear).union(bridge).buffer(0)


# ===========================================================================
# HAZNE (+ sap, gobek)
# ===========================================================================
def _handle(p, z0):
    w, hh = p["HANDLE_W"], p["HANDLE_H"]
    c = hh / 2 - 1.0
    hexa = Polygon([(-w / 2 + c, 0), (w / 2 - c, 0), (w / 2, c), (w / 2, hh - c),
                    (w / 2 - c, hh), (-w / 2 + c, hh), (-w / 2, hh - c), (-w / 2, c)])
    bar = g.extrude(hexa, 0.0, p["HANDLE_L"] + 30.0)
    bar.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    bar.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    bar.apply_translation((p["PIVOT_X"] + 2.0, 0.0, z0))
    bar = g.diff(bar, g.cyl(2.2, -5, 20).apply_translation((p["PIVOT_X"] + p["HANDLE_L"] + 4.0, 0, 0)))
    return g.inter(bar, g.box(0, p["PIVOT_X"] + p["HANDLE_L"] + 10.0, -10, 10, -10, 30))


def _tab_solid(size, p, which, grow=0.0):
    """Kapali konumdaki tirnak (alt: disk ustunden yukari; ust: kapak altindan asagi)."""
    e = grow
    if which == "bottom":
        r_edge = p["FLANGE_R"]
        z0, z1 = 0.0 - e, p["TAB_H"] + e
    else:
        h = cup_depth(size, p)
        r_edge = _r_at(h, p) + p["WALL"] + 1.2
        z0, z1 = h - p["TAB_H"] - e, h + e
    half = np.degrees((p["TAB_W"] / 2) / r_edge)
    return g.sector(r_edge - p["TAB_R"] - e, r_edge + 0.2 + e, 180.0 - half - np.degrees(e / r_edge),
                    180.0 + half + np.degrees(e / r_edge), z0, z1)


def _tab_sweep(size, p, which):
    """Tirnagin kapanmanin son LOCK_DEG derecesinde supurdugu hacim.  Girise
    dogru tavan LOCK_WEDGE kadar yuksektir: disk son derecelerde O-ring'e sikisir."""
    ax, ad = pivot_axis(p)
    sgn = 1.0 if which == "bottom" else -1.0
    parts = []
    n = 16
    for i in range(n + 1):
        f = i / n
        a = f * p["LOCK_DEG"]
        extra = p["LOCK_WEDGE"] * f          # girise dogru (buyuk aci) daha bol
        t = _tab_solid(size, p, which, grow=p["FIT"] / 2)
        # kama: tavani extra kadar yukselt (alt) / alcalt (ust)
        zt = p["TAB_H"] + p["FIT"] / 2 + extra if which == "bottom" else None
        m = t.copy()
        if which == "bottom":
            m = g.union(m, g.movez(t, extra))
        else:
            m = g.union(m, g.movez(t, -extra))
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(sgn * a), ad, ax))
        parts.append(m)
    return g.union(*parts)


def _funnel(p):
    """Govdenin altindaki huni + onu flansa baglayan kanat.
    Ust halka z = -(DISC_T+FUN_GAP)'de; alt disk halka ile flans arasindaki
    yariktan yana kayar.  Kanat +y tarafinda (disk -y'ye dogru acilir)."""
    zt = -(p["DISC_T"] + p["FUN_GAP"])
    ro, w = p["FUN_TOP_RO"], p["FUN_WALL"]
    r_sp = p["SPOUT_D"] / 2
    ri = ro - w * np.sqrt(2.0)                     # 45 derecelik cidar, normal kalinlik w
    z_co = zt - (ro - r_sp)                        # dis koninin bittigi z
    z_ci = zt - (ri - (r_sp - w))
    z_end = z_co - p["SPOUT_L"]
    fun = g.revolve([(r_sp - w, z_end), (r_sp, z_end), (r_sp, z_co), (ro, zt), (ri, zt),
                     (r_sp - w, z_ci)])
    # kanat (r,z profili): ustte flansa 45 derece pahla biner, altta huni
    # cidarinin icine (ic koni cizgisinin 0.3 mm disinda) kadar iner
    fr = p["FIN_RO"]
    zb = zt - 2.9
    fin = g.revolve([(p["FLANGE_R"] - 1.0, 2.5), (p["FLANGE_R"], 2.5), (fr, 0.0), (fr, zb),
                     (ri - (zt - zb) + 0.8, zb), (ri + 0.3, zt), (p["FLANGE_R"] - 1.0, zt)])
    fin = g.inter(fin, g.sector(0, fr + 1, p["FIN_A0"], p["FIN_A1"], zb - 1, 5))
    fin = g.diff(fin, g.cyl(p["FLANGE_R"] + p["FIT"], zt, 0.5))                 # diskin yarigi
    return g.union(fun, fin)


def _lock_housing(size, p):
    """Tunelleri barindiran yerel kalinlasma: onde 70 derecelik yay."""
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]
    fl = g.sector(p["FLANGE_R"] - 3.0, p["FLANGE_R"] + 0.6, 180 - 36, 180 + 36, 0.0, p["TAB_H"] + 1.5)
    top = g.sector(r_o - 1.0, r_o + 1.2 + 0.6, 180 - 36, 180 + 36, h - p["TAB_H"] - 1.5, h)
    # bandin alt kenari 45 derece pahli (agiz yukari baskida destek istemesin)
    cham = g.revolve([(r_o - 1.0, h - p["TAB_H"] - 1.5 - 2.8), (r_o + 1.8, h - p["TAB_H"] - 1.5),
                      (r_o - 1.0, h - p["TAB_H"] - 1.5)])
    top = g.union(top, g.inter(cham, g.sector(0, 40, 180 - 36, 180 + 36, 0, h)))
    return g.union(fl, top)


def _det_bumps(size, p):
    """Centik tumsekleri.  Pivotlu disk radyal esneyemez; bu yuzden tumsek
    DIKEYdir: alt diskin tirnagi tunel TAVANindaki tumsegin altindan gecerken
    disk 0.35 mm asagi iner (O-ring gevser), gecince kama onu tekrar sikar.
    Ust disk icin tumsek tunel TABANindadir, kapak 0.35 mm kalkip gecer.
    Tumsek, tirnagin kapali konumdaki ARKA kenarinin hemen otesindedir."""
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"] + 1.2
    out = []
    for which, r_edge in (("bottom", p["FLANGE_R"]), ("top", r_o)):
        half = np.degrees((p["TAB_W"] / 2) / r_edge)
        # kapanma yonu: alt disk acilirken +z donuyor -> tirnak acilirken buyuk
        # aciya gider, kapanirken kucuk aciya doner: arka kenar 180+half.
        # ust disk ters yonde doner: arka kenar 180-half.
        if which == "bottom":
            a0, a1 = 180.0 + half + 0.5, 180.0 + half + 3.2
            zc = p["TAB_H"] + p["FIT"] / 2                       # tunel tavani
            z0, z1 = zc - p["DET_R"], zc + 0.6
        else:
            a0, a1 = 180.0 - half - 3.2, 180.0 - half - 0.5
            zf = h - p["TAB_H"] - p["FIT"] / 2                   # tunel tabani
            z0, z1 = zf - 0.6, zf + p["DET_R"]
        out.append(g.sector(r_edge - p["TAB_R"] - 0.2, r_edge + 0.4, a0, a1, z0, z1))
    return out


def build_body(size, p=P):
    h = cup_depth(size, p)
    r_rim = _r_at(h, p)
    w = p["WALL"]
    prof = [
        (p["BORE"] / 2, 0.0), (r_rim, h), (r_rim + w, h),
        (r_rim + w, h - p["LID_BEAD_Z"] + 0.6),                  # kapak boncugu
        (r_rim + w + p["LID_BEAD"], h - p["LID_BEAD_Z"] - 0.3),
        (r_rim + w, h - p["LID_BEAD_Z"] - 1.2),
        (p["FLANGE_R"], p["FLANGE_T"] + (p["FLANGE_R"] - p["BORE"] / 2 - w)),   # 45 der.
        (p["FLANGE_R"], 0.0),
    ]
    body = g.union(g.revolve(prof), _funnel(p))
    # mil gobegi: z 0 .. h (ust kapak bunun ustune oturur), sap kokuyle birlesir
    boss = g.cyl(p["BOSS_R"], 0.0, h).apply_translation((p["PIVOT_X"], 0, 0))
    neck = g.extrude(sbox(p["FLANGE_R"] - 3.0, -p["BOSS_R"], p["PIVOT_X"], p["BOSS_R"]), 0.0, h)
    body = g.union(body, boss, neck, _handle(p, h - p["HANDLE_H"]))
    # mil deligi
    body = g.diff(body, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, -5, h + 20).apply_translation((p["PIVOT_X"], 0, 0)))
    # O-ring yuvasi (oturma yuzeyinde)
    body = g.diff(body, g.tube(p["ORING_R"] - p["ORING_GW"] / 2, p["ORING_R"] + p["ORING_GW"] / 2, -0.1, p["ORING_GD"]))
    # --- teget kilit tunelleri ---------------------------------------------
    # on bolgede flans ve agiz bandi kalinlasir (tunel tavani icin), tuneller
    # tirnagin gercek donus yolunun (son LOCK_DEG derece) supurmesiyle oyulur
    body = g.union(body, _lock_housing(size, p))
    body = g.diff(body, _tab_sweep(size, p, which="bottom"), _tab_sweep(size, p, which="top"))
    # centik tumsekleri: tunel tabaninda, sonda
    body = g.union(body, *_det_bumps(size, p))
    # hazne bosluğu en sonda
    top = h + 10.0
    body = g.diff(body, g.revolve([(0, -0.2), (p["BORE"] / 2, -0.2), (p["BORE"] / 2, 0), (r_rim, h),
                                   (_r_at(top, p), top), (0, top)]))
    return max(body.split(only_watertight=False), key=lambda m: abs(m.volume))


# ===========================================================================
# ALT DISK  (baski: ust (conta) yuzu tablada -> tirnaklar yukari)
# ===========================================================================
def build_bottom(p=P, opened=False):
    r = p["FLANGE_R"]
    disc = g.extrude(_disc_plan(r, p), -p["DISC_T"], 0.0)
    # mil deligi + basi icin havsa (bas diskin altina gomulur)
    disc = g.diff(disc, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, -10, 5).apply_translation((p["PIVOT_X"], 0, 0)),
                  g.cyl(p["PIN_D"] / 2 + 2.2, -p["DISC_T"] - 1, -p["DISC_T"] + 1.3).apply_translation((p["PIVOT_X"], 0, 0)))
    clips = [_tab_solid(15, p, "bottom")]           # tirnak boydan bagimsiz
    disc = g.union(disc, *clips)
    if opened:
        ax, ad = pivot_axis(p)
        disc.apply_transform(trimesh.transformations.rotation_matrix(np.radians(p["OPEN_DEG"]), ad, ax))
    return disc


# ===========================================================================
# UST DISK  (baski: ust yuzu tablada -> tirnaklar baskida yukari)
# ===========================================================================
def build_top(size, p=P, opened=False):
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]
    r = r_o + 1.2
    lid = g.extrude(_disc_plan(r, p), h, h + p["DISC_T"])
    lid = g.diff(lid, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, h - 5, h + 10).apply_translation((p["PIVOT_X"], 0, 0)))
    clips = [_tab_solid(size, p, "top")]
    lid = g.union(lid, *clips)
    if opened:
        ax, ad = pivot_axis(p)
        lid.apply_transform(trimesh.transformations.rotation_matrix(-np.radians(p["OPEN_DEG"]), ad, ax))
    return lid


# ===========================================================================
# MIL  (alttan surulur; ust ucu yarikli tirnak, ust diskin ustune klik yapar)
# ===========================================================================
def build_pin(size, p=P):
    h = cup_depth(size, p)
    r = p["PIN_D"] / 2
    L = p["DISC_T"] + h + p["DISC_T"] + 2.6          # disk alti -> ust disk ustu + tirnak
    prof = [(0, 0), (r + 2.0, 0), (r + 2.0, 1.2), (r, 1.2), (r, L - 2.6),
            (r + 0.5, L - 1.8), (r + 0.5, L - 1.3), (r - 0.3, L), (0, L)]
    pin = g.revolve(prof)
    slot = g.box(-0.6, 0.6, -10, 10, L - 5.0, L + 1)
    return g.diff(pin, slot)


build_gasket = B.build_gasket
