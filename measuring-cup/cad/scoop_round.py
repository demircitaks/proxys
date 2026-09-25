"""YUVARLAK kepce, SURGULU taban: hazne ve ust kapak yuvarlak; taban plakasi
sapa dogru duz kayar (tek elle: sapin yanindaki iki cikintiyi basparmakla
geri it -> taban acilir -> geri cek -> klik).

- Ust kapak (disk): sap kokundeki dikey mil etrafinda +y'ye doner; kapatirken
  on kenari fazla tozu super.  On kenarindaki bacak+ayak burundaki dudagin
  altina girer (kapak agza cekilir), yay parmagi + tumsek klik yapar.
- Taban PLAKASI: onu yuvarlak (r 22), arkasi 48 mm genis duz kenarli.  Kenarlari
  pahli; sapin kokundeki iki yan etegin altindaki 45 derecelik DUDAKLARA oturur
  (kizak: kendini ortalar).  O-ring plakayi dudaklara bastirir -> conta her
  yerde esit sikisir.  Plaka sapa dogru TRAVEL kadar kayinca hazne tamamen acilir.
- Plaka kilidi: eteklerin icine kesilmis dikey yay parmaklari (ustten baglı,
  altta serbest), ic yuzlerinde tumsek; plakanin kenarindaki centiklere kapali
  ve acik konumda oturur (klik).  Plaka arkadan tamamen cikarilabilir (temizlik).
- Haznenin alti hafif HUNI: 45 derecelik koni, ucu PCO-1881 pet sise agzina
  giren Ø20.8 boru.  Huni, dudaklar ve on burunla govdeye baglidir.
z = 0 plakanin ust yuzu (taban); z = h ust diskin alt yuzu (agiz).
Baski: hazne AGIZ TABLADA (ters), huni yukari; etekler tabladan yukselir,
dudaklar 45 derece, koni her iki yonde 45 derece -> destek yok.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g
import scoop_slide as B

P = dict(B.P)
P.update(dict(
    FLANGE_R    = 25.8,   # flans etekleri de sarar (|x| < 9'da bindirme)
    FLANGE_T    = 2.4,
    DISC_T      = 2.5,
    PIVOT_X     = 28.5,   # mil ekseni (flansin 4.5 mm disinda, sap kokunde)
    PIN_D       = 4.0,
    BOSS_R      = 5.2,    # mil etrafindaki gobek
    EAR_R       = 6.2,    # disklerin mile uzanan kulagi
    OPEN_DEG    = 120.0,  # ust kapagin acik konumu (98 derecede hazne tamamen acik; 150+ etege carpar)
    ORING_GD    = 1.15,   # yuva derinligi: O-ring 0.35 mm tasar
    SEAL_GAP    = 0.10,   # kapali konumda disk yuzu ile flans arasi (O-ring 0.25 sikisir)
    # --- taban plakasi + raylar ---------------------------------------------------
    PLATE_RF    = 22.0,   # plakanin on yaricapi (O-ring disi 20.8 -> 1.2 pay)
    PLATE_HW    = 24.0,   # plakanin yarim genisligi (duz kenarlar)
    PLATE_X1    = 46.0,   # plakanin arka kenari (kapali)
    TRAVEL      = 42.0,   # acik konum: on kenar x = -22 + 42 = +20 (hazne kenari 19)
    LIP_W       = 1.0,    # dudagin plakanin altina uzanmasi (radyal); plaka pahi buna oturur
    SKIRT_T     = 1.6,    # yan etek kalinligi
    RAIL_X0     = -0.5,   # eteklerin basi
    RAIL_ZB     = -4.5,   # eteklerin alti
    GATE_X      = 56.0,   # etekleri sapa baglayan kapi (ust cubuk) x0; 6 mm genis
    KNOB_Y0     = 7.0,    # itme cikintilari: sapin yaninda |y| 7..13
    KNOB_Y1     = 13.0,
    KNOB_L      = 4.0,
    SFING_X     = 42.0,   # etek yay parmagi (kapali konumda plakanin centigi burada)
    SFING_W     = 3.0,    # parmak genisligi (x)
    SFING_ROOT  = 9.0,    # parmagin ust ucu (baglı) z; alt ucu serbest
    SFING_BUMP  = 0.5,    # tumsek (ice), 45 derece yanakli
    SLIT        = 0.6,
    # --- ust kapak mandali --------------------------------------------------------
    TAB_W       = 14.0,   # rijit tirnagin teget genisligi
    TAB_OUT     = 3.2,    # tirnagin kapak kenarindan disari tasmasi
    FINGER_L    = 10.0,   # yay parmagi uzunlugu (teget)
    LEG_T       = 1.2,    # ust kapak bacagi = parmagi kalinligi
    LEG_H       = 3.4,    # bacagin agiz duzleminden asagi sarkmasi
    FOOT_T      = 0.8,    # ayak kalinligi (dudagin altina giren)
    BUMP        = 0.6,    # centik tumsegi yuksekligi (45 derece yanakli)
    BUMP_W      = 2.4,    # tumsek tabani
    FINGER_CLR  = 0.6,    # parmagin iceri esneme payi (kanalda)
    LOCK_DEG    = 14.0,   # kanalin acisal uzunlugu (kapanmanin son 14 derecesi)
    WEDGE_TOP   = 0.40,   # ust dudak alti rampasi (giriste bu kadar yuksek)
    POST_HALF   = 22.0,   # burnun yarim acisi (pivot etrafinda, 180 merkezli)
    POST_SKIRT  = 1.5,    # kanal dis duvari (tumsek yuvasi bunun icinde)
    # --- sap: ust yuzu agiz duzleminde (ters baskida tablada) ------------------
    HANDLE_L    = 86.0,
    HANDLE_W    = 12.0,
    HANDLE_H    = 8.0,
    # --- huni (govdenin alti) --------------------------------------------------
    FUN_GAP     = 0.1,    # plakanin alti ile huni ust halkasi arasi (halka plakayi tasir)
    FUN_TOP_RO  = 24.6,   # huni ust halkasi dis yaricap
    FUN_WALL    = 1.4,
    SPOUT_D     = 20.8,   # PCO-1881 ic capi 21.74 -> 0.47 mm/yan bosluk
    SPOUT_L     = 7.0,    # boynun icine giren duz kisim
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
    """Govdenin altindaki huni (kanat yok: dudaklar ve on burun tasir)."""
    zt, ro, w, r_sp, ri, z_co, z_ci, z_end = _fun_dims(p)
    return g.revolve([(r_sp - w, z_end), (r_sp, z_end), (r_sp, z_co), (ro, zt), (ri, zt),
                      (r_sp - w, z_ci)])


def _post_rout(size, p):
    h = cup_depth(size, p)
    r_o = _r_at(h, p) + p["WALL"]
    return p["PIVOT_X"] + r_o + 2.2 + p["LEG_T"] + p["FIT"] / 2 + p["POST_SKIRT"]


def _post(size, p):
    """Burun: onde, pivot merkezli dilim; yalniz ust kapagin mandal kanali icin
    (agizdan LEG_H+2 asagi).  Dis yuzu pivot dairesidir (kanal duvarina esmerkezli)."""
    h = cup_depth(size, p)
    ro = _post_rout(size, p)
    a0, a1 = 180 - p["POST_HALF"], 180 + p["POST_HALF"]
    return g.extrude(_parc(p, 40.0, ro, a0, a1), h - p["LEG_H"] - 2.0, h)


def _extrude_x(poly_yz, x0, x1):
    """(y,z) profilini x boyunca katiya cevirir."""
    m = g.extrude(poly_yz, 0.0, x1 - x0)
    m.apply_transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))
    return m


def _rails(size, p):
    """Iki yan etek (RAIL_ZB..h, ters baskida tabladan yukselir) + altlarinda
    45 derece egimli dudaklar + etekleri sapa baglayan kapi cubugu (agiz duzleminde)."""
    h = cup_depth(size, p)
    yi = p["PLATE_HW"] + p["FIT"] / 2
    yo = yi + p["SKIRT_T"]
    li = p["PLATE_HW"] - p["LIP_W"]
    zl = -p["DISC_T"] - p["SEAL_GAP"]                    # dudak ucu (plaka bunun 0.1 ustunde)
    zb = p["RAIL_ZB"]
    x0, x1 = p["RAIL_X0"], p["PLATE_X1"] + p["TRAVEL"] + 2.0
    prof = Polygon([(li, zb), (yo, zb), (yo, h), (yi, h), (yi, zl + (yi - li)), (li, zl)])
    parts = [_extrude_x(prof, x0, x1)]
    prof_m = Polygon([(-y, z) for y, z in prof.exterior.coords])
    parts.append(_extrude_x(prof_m, x0, x1))
    parts.append(g.box(p["GATE_X"], p["GATE_X"] + 6.0, -yo, yo, h - 3.0, h))
    return g.union(*parts)


def _skirt_slits(size, p):
    """Etek yay parmaklarini olusturan dikey yariklar (her iki etekte)."""
    yi = p["PLATE_HW"] + p["FIT"] / 2
    yo = yi + p["SKIRT_T"]
    x0 = p["SFING_X"]
    cuts = []
    for sgn in (1, -1):
        for xa in (x0 - p["SLIT"], x0 + p["SFING_W"]):
            cuts.append(g.box(xa, xa + p["SLIT"], min(sgn * (yi - 0.5), sgn * (yo + 0.5)),
                              max(sgn * (yi - 0.5), sgn * (yo + 0.5)), p["RAIL_ZB"] - 1, p["SFING_ROOT"]))
    return cuts


def _skirt_bumps(p, grow=0.0):
    """Parmaklarin ic yuzundeki tumsekler (x'te 45 derece yanakli); grow>0 -> plakadaki centik."""
    yi = p["PLATE_HW"] + p["FIT"] / 2
    b, e = p["SFING_BUMP"], grow
    x0, x1 = p["SFING_X"] - e, p["SFING_X"] + p["SFING_W"] + e
    out = []
    for sgn in (1, -1):
        pts = [(x0, yi + 0.3), (x0 + b, yi - b - e), (x1 - b, yi - b - e), (x1, yi + 0.3)]
        out.append(g.extrude(Polygon([(x, sgn * y) for x, y in pts]), -1.0 - e, 0.0 + e))
    return out


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


def build_body(size, p=P, bumps=True):
    h = cup_depth(size, p)
    r_rim = _r_at(h, p)
    w = p["WALL"]
    wall = g.revolve([(p["BORE"] / 2, 0.0), (r_rim, h), (r_rim + w, h), (r_rim + w, 0.0)])
    fl_r = p["FLANGE_R"]
    flange = g.revolve([(p["BORE"] / 2, 0.0), (fl_r, 0.0), (fl_r, fl_r - p["BORE"] / 2 - w + p["FLANGE_T"]),
                        (p["BORE"] / 2, 2 * fl_r - p["BORE"] - w + p["FLANGE_T"])])     # 45 derece pah
    body = g.union(wall, flange, _funnel(p), _post(size, p), _rails(size, p))
    # mil gobegi: z 0 .. h (ust kapak bunun ustune oturur), sap kokuyle birlesir
    boss = g.cyl(p["BOSS_R"], 0.0, h).apply_translation((p["PIVOT_X"], 0, 0))
    neck = g.extrude(sbox(fl_r - 3.0, -p["BOSS_R"], p["PIVOT_X"], p["BOSS_R"]), 0.0, h)
    body = g.union(body, boss, neck, _handle(p, h - p["HANDLE_H"]))
    # mil deligi + basi icin gobek altinda havsa (plaka basin altindan gecer, mili tutar)
    body = g.diff(body, g.cyl(p["PIN_D"] / 2 + p["FIT"] / 2, -5, h + 20).apply_translation((p["PIVOT_X"], 0, 0)),
                  g.cyl(p["PIN_D"] / 2 + 2.0 + p["FIT"] / 2, -1, 1.3).apply_translation((p["PIVOT_X"], 0, 0)))
    # O-ring yuvasi (oturma yuzeyinde)
    body = g.diff(body, g.tube(p["ORING_R"] - p["ORING_GW"] / 2, p["ORING_R"] + p["ORING_GW"] / 2, -0.1, p["ORING_GD"]))
    # ust mandal kanali (burna oyulur), etek yariklari, etek tumsekleri
    body = g.diff(body, _top_channel(size, p), *_skirt_slits(size, p))
    if bumps:
        body = g.union(body, *_skirt_bumps(p))
    # hazne bosluğu en sonda
    top = h + 10.0
    body = g.diff(body, g.revolve([(0, -0.2), (p["BORE"] / 2, -0.2), (p["BORE"] / 2, 0), (r_rim, h),
                                   (_r_at(top, p), top), (0, top)]))
    return max(body.split(only_watertight=False), key=lambda m: abs(m.volume))


# ===========================================================================
# TABAN PLAKASI  (baski: conta yuzu tablada, itme cikintilari yukari)
# ===========================================================================
def build_plate(size, p=P, opened=False, notches=True):
    h = cup_depth(size, p)
    hw, t = p["PLATE_HW"], p["DISC_T"]
    plan = Point(0, 0).buffer(p["PLATE_RF"], resolution=128).union(sbox(0.0, -hw, p["PLATE_X1"], hw)).buffer(0)
    plate = g.extrude(plan, -t, 0.0)
    # duz kenarlarin alt pahi: (hw-LIP_W-0.15, -t) -> 45 derece, dudagin egiminin 0.18 mm ustunde
    c0 = hw - p["LIP_W"] - 0.15
    cham = Polygon([(c0 - 0.1, -t - 0.1), (c0, -t), (hw + 0.3, -t + (hw + 0.3 - c0)), (hw + 0.6, -t + (hw + 0.3 - c0)),
                    (hw + 0.6, -t - 0.1)])
    plate = g.diff(plate, _extrude_x(cham, -1.0, p["PLATE_X1"] + 1.0),
                   _extrude_x(Polygon([(-y, z) for y, z in cham.exterior.coords]), -1.0, p["PLATE_X1"] + 1.0))
    # itme cikintilari (sapin iki yaninda, kapi cubugunun altindan gecer)
    for sgn in (1, -1):
        plate = g.union(plate, g.box(p["PLATE_X1"] - p["KNOB_L"], p["PLATE_X1"], sgn * p["KNOB_Y0"], sgn * p["KNOB_Y1"],
                                     -0.5, h - 3.5))
    if notches:                                             # kapali (x = SFING_X) ve acik (x - TRAVEL)
        for dx in (0.0, -p["TRAVEL"]):
            plate = g.diff(plate, *[b.apply_translation((dx, 0, 0)) for b in _skirt_bumps(p, grow=p["FIT"] / 2)])
    if opened:
        plate.apply_translation((p["TRAVEL"], 0, 0))
    return plate


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
