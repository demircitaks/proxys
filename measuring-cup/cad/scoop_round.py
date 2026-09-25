"""YUVARLAK kepce: alt ve ust kapak birer disk, sap kokundeki tek dikey mil
etrafinda yana DONER.  Ray, kanal, kizak yok; siluet bastan sona yuvarlak.

- Ust kapak (disk) kapatilirken on kenari fazla tozu super -> silme.
- Alt disk tabandir; kapaliyken O-ring'e oturur.  Acmak icin diski sapin
  altina dogru cevirirsiniz.  Ikisi de ayni mile takilir.
- MANDAL: her kapagin on kenarinda rijit bir tirnak, tirnagin yanindan teget
  uzanan bir yay parmagi ve parmagin ucunda tumsek vardir.  Govdenin onunde
  bir "burun" (post) bulunur; tirnak kapanmanin son LOCK_DEG derecesinde
  burnun icindeki C-kanala girer.  Alt kanalin tabani rampalidir (kama):
  disk O-ring'e dogru itilir.  Ust kapagin tirnagi asagi sarkan bir bacak +
  iceri bakan ayaktir; ayak burundaki dudagin altina girer, dudagin alti
  rampalidir: kapak agza cekilir.  Parmagin tumsegi kapali konumda kanal dis
  duvarindaki yuvaya oturur (centik, klik); acarken parmak ~0.45 mm iceri
  esneyerek gecer.  Yay = parmagin kendisi, O-ring'e veya diske bagli degil.
- Haznenin alti hafif HUNI: 45 derecelik koni, ucu PCO-1881 pet sise agzina
  giren Ø20.8 boru.  Alt disk huninin ustundeki yariktan yana kayar; huni
  govdeye +y tarafindaki kanatla baglidir (diskin supurmedigi taraf).
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
    ORING_GD    = 1.15,   # yuva derinligi: O-ring 0.35 mm tasar
    SEAL_GAP    = 0.10,   # kapali konumda disk yuzu ile flans arasi (O-ring 0.25 sikisir)
    # --- mandal ---------------------------------------------------------------
    TAB_W       = 14.0,   # rijit tirnagin teget genisligi
    TAB_OUT     = 3.2,    # tirnagin kapak kenarindan disari tasmasi
    FINGER_L    = 10.0,   # yay parmagi uzunlugu (teget)
    FINGER_T    = 1.5,    # alt disk parmagi kalinligi (radyal)
    LEG_T       = 1.2,    # ust kapak bacagi = parmagi kalinligi
    LEG_H       = 3.4,    # bacagin agiz duzleminden asagi sarkmasi
    FOOT_T      = 0.8,    # ayak kalinligi (dudagin altina giren)
    BUMP        = 0.6,    # centik tumsegi yuksekligi (45 derece yanakli)
    BUMP_W      = 2.4,    # tumsek tabani
    FINGER_CLR  = 0.6,    # parmagin iceri esneme payi (kanalda)
    LOCK_DEG    = 14.0,   # kanalin acisal uzunlugu (kapanmanin son 14 derecesi)
    WEDGE       = 0.35,   # alt kanal tabani rampasi (giriste bu kadar alcak)
    WEDGE_TOP   = 0.40,   # ust dudak alti rampasi (giriste bu kadar yuksek)
    POST_HALF   = 22.0,   # burnun yarim acisi (pivot etrafinda, 180 merkezli)
    SKIRT_T     = 1.5,    # kanal dis duvari (tumsek yuvasi bunun icinde)
    POST_ZB     = -4.0,   # burnun alt yuzu
    # --- sap: ust yuzu agiz duzleminde (ters baskida tablada) ------------------
    HANDLE_L    = 86.0,
    HANDLE_W    = 12.0,
    HANDLE_H    = 8.0,
    # --- huni (govdenin alti) --------------------------------------------------
    FUN_GAP     = 0.6,    # alt diskin alti ile huni ust halkasi arasi
    FUN_TOP_RO  = 24.6,   # huni ust halkasi dis yaricap
    FUN_WALL    = 1.4,
    SPOUT_D     = 20.8,   # PCO-1881 ic capi 21.74 -> 0.47 mm/yan bosluk
    SPOUT_L     = 7.0,    # boynun icine giren duz kisim
    FIN_A0      = 40.0,   # baglanti kanadi (+y tarafi), acisal araligi
    FIN_A1      = 130.0,
    FIN_RO      = 26.5,
))
SIZES = B.SIZES
cup_depth, _r_at, brim_volume, report = B.cup_depth, B._r_at, B.brim_volume, B.report


def pivot_axis(p=P):
    return [p["PIVOT_X"], 0.0, 0.0], [0.0, 0.0, 1.0]


def _rot(mesh, deg, p=P):
    ax, ad = pivot_axis(p)
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), ad, ax))
    return m


def _arc(r0, r1, a0, a1):
    """Halka dilimi plani (shapely)."""
    if a1 < a0:
        a0, a1 = a1, a0
    n = max(6, int((a1 - a0) / 1.5) + 2)
    a = np.radians(np.linspace(a0, a1, n))
    return Polygon([(r1 * np.cos(t), r1 * np.sin(t)) for t in a] +
                   [(r0 * np.cos(t), r0 * np.sin(t)) for t in a[::-1]])


def _disc_plan(r_disc, p=P):
    """Disk + mile uzanan kulak (tek parca plan)."""
    disc = Point(0, 0).buffer(r_disc, resolution=128)
    ear = Point(p["PIVOT_X"], 0).buffer(p["EAR_R"], resolution=48)
    bridge = sbox(r_disc - 6.0, -p["EAR_R"], p["PIVOT_X"], p["EAR_R"])
    return disc.union(ear).union(bridge).buffer(0)


def _parc(p, r0, r1, a0, a1):
    """PIVOT merkezli halka dilimi plani (mandal geometrisi pivot yaylaridir:
    kapak pivot etrafinda dondugu icin kanal duvari ile parmak arasi sabit kalir)."""
    from shapely.affinity import translate
    return translate(_arc(r0, r1, a0, a1), p["PIVOT_X"], 0.0)


def _latch_plan(p, r_far, sgn, ft):
    """Mandalin PLANI (kapali konum).  r_far = kapagin on kenarinin pivota
    uzakligi (PIVOT_X + kapak yaricapi).  Butun yaylar pivot merkezlidir.
    tirnak: pivot yaricapi r_far-4 .. r_far+TAB_OUT, TAB_W genisliginde, 180 etrafinda.
    parmak: tirnagin bir kenarindan teget uzanan ft kalinliginda serit
    (dis yuzu tirnagin dis yuzuyle ayni pivot dairesinde), ucunda 45 derece
    yanakli tumsek.  sgn=+1: parmak 180'den buyuk pivot acilarinda (alt disk
    -y'ye acilir), sgn=-1: 180'den kucuk (ust kapak +y'ye acilir)."""
    r0, r1 = r_far - 4.0, r_far + p["TAB_OUT"]
    half = np.degrees(p["TAB_W"] / 2 / r1)
    tab = _parc(p, r0, r1, 180 - half, 180 + half)
    f0, f1 = r1 - ft, r1
    a_root = 180 + sgn * (half - 0.3)                       # tirnaga bindir
    a_tip = 180 + sgn * (half + np.degrees(p["FINGER_L"] / f1))
    finger = _parc(p, f0, f1, a_root, a_tip)
    bw = np.degrees(p["BUMP_W"] / f1)
    db = np.degrees(p["BUMP"] / f1)
    b1 = a_tip - sgn * 0.2
    b0 = b1 - sgn * bw
    pts = [(f1 - 0.3, b0), (f1 + p["BUMP"], b0 + sgn * db), (f1 + p["BUMP"], b1 - sgn * db), (f1 - 0.3, b1)]
    bump = Polygon([(p["PIVOT_X"] + r * np.cos(np.radians(a)), r * np.sin(np.radians(a))) for r, a in pts])
    clr = _parc(p, f0 - p["FINGER_CLR"], f1, a_root, a_tip)  # parmagin esneme payi
    return dict(tab=tab, finger=finger, bump=bump, clear=clr, half=half, r1=r1, a_tip=a_tip)


# ===========================================================================
# HAZNE (+ huni, burun, sap, gobek)
# ===========================================================================
def _fun_dims(p):
    zt = -(p["DISC_T"] + p["FUN_GAP"])
    ro, w = p["FUN_TOP_RO"], p["FUN_WALL"]
    r_sp = p["SPOUT_D"] / 2
    ri = ro - w * np.sqrt(2.0)                     # 45 derecelik cidar, normal kalinlik w
    z_co = zt - (ro - r_sp)                        # dis koninin bittigi z
    z_ci = zt - (ri - (r_sp - w))
    z_end = z_co - p["SPOUT_L"]
    return zt, ro, w, r_sp, ri, z_co, z_ci, z_end


def _funnel_void(p):
    """Huninin ici (toz yolu) + 0.3 mm pay; burun bunun disinda kalir."""
    zt, ro, w, r_sp, ri, z_co, z_ci, z_end = _fun_dims(p)
    return g.revolve([(0, zt + 1), (ri + 0.3, zt + 1), (ri + 0.3, zt), (r_sp - w + 0.3, z_ci),
                      (r_sp - w + 0.3, z_end - 1), (0, z_end - 1)])


def _funnel(p):
    """Govdenin altindaki huni + onu flansa baglayan kanat (+y tarafi)."""
    zt, ro, w, r_sp, ri, z_co, z_ci, z_end = _fun_dims(p)
    fun = g.revolve([(r_sp - w, z_end), (r_sp, z_end), (r_sp, z_co), (ro, zt), (ri, zt),
                     (r_sp - w, z_ci)])
    fr = p["FIN_RO"]
    zb = zt - 2.9
    fin = g.revolve([(p["FLANGE_R"] - 1.0, 2.5), (p["FLANGE_R"], 2.5), (fr, 0.0), (fr, zb),
                     (ri - (zt - zb) + 0.8, zb), (ri + 0.3, zt), (p["FLANGE_R"] - 1.0, zt)])
    fin = g.inter(fin, g.sector(0, fr + 1, p["FIN_A0"], p["FIN_A1"], zb - 1, 5))
    fin = g.diff(fin, g.cyl(p["FLANGE_R"] + p["FIT"], zt, 0.5))                 # diskin yarigi
    return g.union(fun, fin)


def _post_rout(size, p):
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]
    return p["PIVOT_X"] + max(p["FLANGE_R"] + p["TAB_OUT"], r_o + 2.2 + p["LEG_T"]) + p["FIT"] / 2 + p["SKIRT_T"]


def _post(size, p):
    """Burun: pivot merkezli dilim.  Ust kisim (z 0..h) cidara kadar dolu,
    alt kisim (POST_ZB..0) yalniz tirnak yolunun altindaki dudak halkasi.
    Kanallar buna oyulur; dis yuzu pivot dairesidir (kanal duvarina esmerkezli)."""
    h = cup_depth(size, p)
    ro = _post_rout(size, p)
    a0, a1 = 180 - p["POST_HALF"], 180 + p["POST_HALF"]
    up = g.extrude(_parc(p, 40.0, ro, a0, a1), 0.0, h)
    lo = g.extrude(_parc(p, p["PIVOT_X"] + p["FLANGE_R"] - 2.0, ro, a0, a1), p["POST_ZB"], 0.0)
    return g.diff(g.union(up, lo), _funnel_void(p))


def _handle(p, z0):
    w, hh = p["HANDLE_W"], p["HANDLE_H"]
    c = hh / 2 - 1.0
    hexa = Polygon([(-w / 2 + c, 0), (w / 2 - c, 0), (w / 2, c), (w / 2, hh - c),
                    (w / 2 - c, hh), (-w / 2 + c, hh), (-w / 2, hh - c), (-w / 2, c)])
    bar = g.extrude(hexa, 0.0, p["HANDLE_L"] + 30.0)
    bar.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    bar.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    bar.apply_translation((p["PIVOT_X"] + 2.0, 0.0, z0))
    bar = g.diff(bar, g.cyl(2.2, -5, 40).apply_translation((p["PIVOT_X"] + p["HANDLE_L"] + 4.0, 0, 0)))
    return g.inter(bar, g.box(0, p["PIVOT_X"] + p["HANDLE_L"] + 10.0, -10, 10, -10, 40))


def _disc_sweep(p, steps=30):
    """Alt disk govdesinin (r FLANGE_R + FIT/2) 0..75 derecede supurdugu yarik:
    disk pivot etrafinda dondugu icin -y tarafinda r 24'u asar; burun bununla oyulur."""
    zt = _fun_dims(p)[0]
    d = g.extrude(Point(0, 0).buffer(p["FLANGE_R"] + p["FIT"] / 2, resolution=96), zt + 0.02, 0.0)
    return g.union(*[_rot(d, a, p) for a in np.linspace(0.0, 75.0, steps)])


def _bottom_channel(p, steps=44):
    """Alt tirnak + parmagin (tumseksiz, FIT/2 buyutulmus) kapanmanin son
    LOCK_DEG+14 derecesinde supurdugu hacim.  Taban kapali konumda
    -DISC_T-SEAL_GAP'te, girise dogru WEDGE kadar alcalir.  Sonda tumsek yuvasi."""
    L = _latch_plan(p, p["PIVOT_X"] + p["FLANGE_R"], +1, p["FINGER_T"])
    plan = L["tab"].union(L["clear"]).buffer(p["FIT"] / 2)
    z0, z1 = -p["DISC_T"] - p["SEAL_GAP"], p["FIT"] / 2
    parts = []
    for a in np.linspace(0.0, p["LOCK_DEG"] + 30.0, steps):
        extra = p["WEDGE"] * min(1.0, a / p["LOCK_DEG"])
        parts.append(_rot(g.extrude(plan, z0 - extra, z1), a, p))
    pocket = g.extrude(L["bump"].buffer(p["FIT"] / 2), z0 - 0.3, z1)
    return g.union(*parts, pocket)


def _top_latch(size, p, bump=True, e=0.0, e_top=None, clear=False, open_top=False):
    """Ust kapagin mandali (kapali konum, 3B): bacak + ayak + parmak (+ tumsek).
    e: buyutme payi (kanal icin); e_top: ayagin ust yuzu icin ayri pay;
    clear: parmagin esneme payini da ekle; open_top: bacak/parmak yuvasi ustte acik."""
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]
    leg0 = p["PIVOT_X"] + r_o + 2.2                        # pivot yaricaplari
    leg1 = leg0 + p["LEG_T"]
    L = _latch_plan(p, leg1 - p["TAB_OUT"], -1, p["LEG_T"])
    e_top = e if e_top is None else e_top
    zb = h - p["LEG_H"]
    half = L["half"] + np.degrees(e / leg1)
    z_top = h + 0.5 if open_top else h + 0.05
    leg = g.extrude(_parc(p, leg0 - e, leg1 + e, 180 - half, 180 + half), zb - e, z_top)
    foot = g.extrude(_parc(p, p["PIVOT_X"] + r_o + 0.4 - e, leg0 + e, 180 - half, 180 + half),
                     zb - e, zb + p["FOOT_T"] + e_top)
    fp = L["clear"] if clear else L["finger"]
    finger = g.extrude(fp.buffer(e), zb - e, (z_top if open_top else h - 0.3))
    parts = [leg, foot, finger]
    if bump:
        parts.append(g.extrude(L["bump"].buffer(e), zb - e, (z_top if open_top else h - 0.3)))
    return g.union(*parts)


def _top_channel(size, p, steps=44):
    """Ust mandalin supurdugu hacim: dudagin alti girise dogru WEDGE_TOP yukselir."""
    t = _top_latch(size, p, bump=False, e=p["FIT"] / 2, e_top=0.05, clear=True, open_top=True)
    parts = []
    for a in np.linspace(0.0, p["LOCK_DEG"] + 30.0, steps):
        extra = p["WEDGE_TOP"] * min(1.0, a / p["LOCK_DEG"])
        parts.append(_rot(g.union(t, g.movez(t, extra)), -a, p))
    h = cup_depth(size, p)
    L = _latch_plan(p, p["PIVOT_X"] + _r_at(h, p) + p["WALL"] + 2.2 + p["LEG_T"] - p["TAB_OUT"], -1, p["LEG_T"])
    pocket = g.extrude(L["bump"].buffer(p["FIT"] / 2), h - p["LEG_H"] - 0.3, h + 0.5)
    return g.union(*parts, pocket)


def build_body(size, p=P):
    h = cup_depth(size, p)
    r_rim = _r_at(h, p)
    w = p["WALL"]
    wall = g.revolve([(p["BORE"] / 2, 0.0), (r_rim, h), (r_rim + w, h), (r_rim + w, 0.0)])
    fl_r = p["FLANGE_R"]
    flange = g.revolve([(p["BORE"] / 2, 0.0), (fl_r, 0.0), (fl_r, fl_r - p["BORE"] / 2 - w + p["FLANGE_T"]),
                        (p["BORE"] / 2, 2 * fl_r - p["BORE"] - w + p["FLANGE_T"])])     # 45 derece pah
    body = g.union(wall, flange, _funnel(p), _post(size, p))
    # mil gobegi: z 0 .. h (ust kapak bunun ustune oturur), sap kokuyle birlesir
    boss = g.cyl(p["BOSS_R"], 0.0, h).apply_translation((p["PIVOT_X"], 0, 0))
    neck = g.extrude(sbox(fl_r - 3.0, -p["BOSS_R"], p["PIVOT_X"], p["BOSS_R"]), 0.0, h)
    body = g.union(body, boss, neck, _handle(p, h - p["HANDLE_H"]))
    # mil deligi
    body = g.diff(body, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, -5, h + 20).apply_translation((p["PIVOT_X"], 0, 0)))
    # O-ring yuvasi (oturma yuzeyinde)
    body = g.diff(body, g.tube(p["ORING_R"] - p["ORING_GW"] / 2, p["ORING_R"] + p["ORING_GW"] / 2, -0.1, p["ORING_GD"]))
    # mandal kanallari (burna oyulur)
    body = g.diff(body, _disc_sweep(p), _bottom_channel(p), _top_channel(size, p))
    # hazne bosluğu en sonda
    top = h + 10.0
    body = g.diff(body, g.revolve([(0, -0.2), (p["BORE"] / 2, -0.2), (p["BORE"] / 2, 0), (r_rim, h),
                                   (_r_at(top, p), top), (0, top)]))
    return max(body.split(only_watertight=False), key=lambda m: abs(m.volume))


# ===========================================================================
# ALT DISK  (baski: alt yuzu tablada; tirnak ve parmak disk duzleminde)
# ===========================================================================
def build_bottom(p=P, opened=False, bump=True):
    L = _latch_plan(p, p["PIVOT_X"] + p["FLANGE_R"], +1, p["FINGER_T"])
    plan = _disc_plan(p["FLANGE_R"], p).union(L["tab"]).union(L["finger"])
    if bump:
        plan = plan.union(L["bump"])
    disc = g.extrude(plan.buffer(0), -p["DISC_T"], 0.0)
    # mil deligi + basi icin havsa (bas diskin altina gomulur)
    disc = g.diff(disc, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, -10, 5).apply_translation((p["PIVOT_X"], 0, 0)),
                  g.cyl(p["PIN_D"] / 2 + 2.2, -p["DISC_T"] - 1, -p["DISC_T"] + 1.3).apply_translation((p["PIVOT_X"], 0, 0)))
    return _rot(disc, p["OPEN_DEG"], p) if opened else disc


# ===========================================================================
# UST DISK  (baski: ust yuzu tablada -> bacak, ayak, parmak yukari)
# ===========================================================================
def build_top(size, p=P, opened=False, bump=True):
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]
    L = _latch_plan(p, p["PIVOT_X"] + r_o + 2.2 + p["LEG_T"] - p["TAB_OUT"], -1, p["LEG_T"])
    plan = _disc_plan(r_o + 1.2, p).union(L["tab"]).buffer(0)
    lid = g.union(g.extrude(plan, h, h + p["DISC_T"]), _top_latch(size, p, bump=bump))
    lid = g.diff(lid, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, h - 5, h + 10).apply_translation((p["PIVOT_X"], 0, 0)))
    return _rot(lid, -p["OPEN_DEG"], p) if opened else lid


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


def build_gasket(p=P):
    return B.build_gasket(p)
