"""SURGULU toz olcegi -- tabani geriye kayan tek plaka.

Fikir (kullanicinin gosterdigi urun): kap kapali bir kovadir; altinda tek bir
plaka vardir; plaka sapa dogru kayinca taban acilir.  Asagi sarkan hicbir sey,
kutu, yay, mil yoktur.

Koordinatlar: z = 0 plakanin ust yuzu = kabin tabani = sizdirmazlik duzlemi.
+x sap yonu.  Plaka +x yonunde TRAVEL kadar kayar.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box as sbox

import geom as g

P = dict(
    # --- hazne ------------------------------------------------------------
    BORE        = 38.0,   # tabandaki ic cap (= bosaltma acikligi)
    DRAFT       = 7.0,    # derece; yukari dogru genisler (daldirma + serbest cikis)
    WALL        = 2.4,
    RIM_CHAM    = 0.6,

    # --- flans / plaka kanallari -------------------------------------------
    FLANGE_R    = 24.0,   # alt flans (oturma bilezigi + kanal duvarlari)
    FLANGE_T    = 2.4,
    BAND_R      = 24.2,   # sap bileziginin kavradigi band
    BAND_Z0     = 2.8,    # alcak tutuldu: 15 mL kabinda ustte KAPAK icin yer kalsin
    BAND_Z1     = 6.2,

    # --- ust kapak (saklama) ----------------------------------------------
    LID_BEAD    = 0.7,    # agzin altindaki kilit boncugu (radyal)
    LID_BEAD_Z  = 3.0,    # agizdan asagi mesafesi (merkez)
    LID_SKIRT   = 4.6,    # kapak etegi boyu
    LID_T       = 2.0,
    LID_PLUG    = 1.8,    # kabin icine giren sizdirmazlik halkasi boyu

    # --- pet sise disi (PCO-1881 / 1810) ----------------------------------
    THR_PITCH   = 2.7,
    THR_TURNS   = 1.6,
    THR_SKIRT_ID= 28.6,   # kapak etegi ic capi (sise dis crest 27.43)
    THR_CREST_D = 25.9,   # dis sirtinin ic capi (sise kok 24.94 ile crest arasi)
    THR_H       = 1.4,    # dis sirti eksenel kalinligi
    CAP_H       = 12.0,   # dis bolgesi yuksekligi
    VENT_N      = 4,
    PLATE_T     = 2.0,
    PLATE_HW    = 21.0,   # plakanin yari genisligi; O-ring cemberini (r 19.9) tamamen orter
    GROOVE_LIP  = 1.8,    # kanal dudaginin plaka altina giren genisligi
    GROOVE_WALL = 2.4,
    LIP_T       = 0.8,    # dudak kalinligi
    FIT         = 0.30,
    WEDGE       = 0.50,   # kapanirken plakayi yukari sikan rampa (= O-ring sikistirma)
    WEDGE_LEN   = 8.0,

    # --- O-ring: oturma bileziginde yuva; plaka kapaninca uzerine sikisir ----
    ORING_R     = 19.9,   # cember yaricapi (ID 38 x kesit 1.5 standart O-ring)
    ORING_CS    = 1.5,
    ORING_GW    = 1.75,   # yuva genisligi
    ORING_GD    = 1.05,   # yuva derinligi -> 0.45 mm disarida kalir, kama onu sikar

    # --- surgu -------------------------------------------------------------
    TRAVEL      = 34.0,   # plaka gozenegi neredeyse tamamen bosaltir
    PLATE_BACK  = 40.0,   # plakanin kapali konumda arkaya uzandigi x
    ARM_X0      = 40.0,   # uzengi kollari
    ARM_X1      = 46.0,
    ARM_Y0      = 18.0,
    ARM_Y1      = 21.0,
    ARM_TOP     = 24.5,
    GABLE_H     = 5.5,    # uzengi ustundeki bastirma yuzeyi (45 derece cati)

    # --- sap (ayri parca, iki boyda ortak) --------------------------------
    COLLAR_T    = 3.4,
    NECK_X1     = 62.0,   # boyun bu x'e kadar dar (uzengi yanindan gecer)
    NECK_HW     = 11.5,
    NECK_TOP    = 20.5,
    GRIP_HW     = 12.5,
    GRIP_TOP    = 23.0,   # uzengi catisi (24.5) kavramanin ustunden gecer
    HANDLE_L    = 82.0,
    SNAP_N      = 2,
    SNAP_R      = 0.9,

    # --- huni (15 mL / pet sise) ------------------------------------------
    FUN_MOUTH   = 52.0,
    FUN_OUT_D   = 21.0,   # huninin sise agzina bakan cikisi (sise kovani 21.74)
    FUN_CONE_A  = 35.0,
)
SIZES = (15, 30)


# ===========================================================================
# hacim (silme)
# ===========================================================================
def _r_at(z, p=P):
    return p["BORE"] / 2.0 + z * np.tan(np.radians(p["DRAFT"]))


def brim_volume(h, p=P):
    rb, t = p["BORE"] / 2.0, np.tan(np.radians(p["DRAFT"]))
    return np.pi * (rb * rb * h + rb * t * h * h + t * t * h ** 3 / 3.0)


def cup_depth(v_ml, p=P):
    lo, hi = 0.1, 300.0
    for _ in range(200):
        m = (lo + hi) / 2.0
        lo, hi = (m, hi) if brim_volume(m, p) < v_ml * 1000.0 else (lo, m)
    return (lo + hi) / 2.0


def report(p=P):
    return [dict(ml=v, depth=cup_depth(v, p), check=brim_volume(cup_depth(v, p), p) / 1000.0,
                 hd=cup_depth(v, p) / p["BORE"], rim_d=2 * _r_at(cup_depth(v, p), p))
            for v in SIZES]


# ===========================================================================
# PARCA 1 -- HAZNE  (baski: AGIZ TABLADA; tup oldugu icin tavani yoktur)
# ===========================================================================
def body_profile(size, p=P):
    h = cup_depth(size, p)
    rb, w = p["BORE"] / 2.0, p["WALL"]
    r_rim = _r_at(h, p)
    d45 = p["BAND_R"] - (_r_at(p["BAND_Z1"], p) + w)           # 45 derece icin yukseklik
    return [
        (rb, 0.0),
        (r_rim, h),
        (r_rim + w - p["RIM_CHAM"], h),
        (r_rim + w, h - p["RIM_CHAM"]),
        (r_rim + w, h - p["LID_BEAD_Z"] + 0.5),                     # kapak boncugu
        (r_rim + w + p["LID_BEAD"], h - p["LID_BEAD_Z"] - 0.2),      # (45 derece flanklar)
        (r_rim + w, h - p["LID_BEAD_Z"] - 0.9),
        (_r_at(p["BAND_Z1"] + d45, p) + w, p["BAND_Z1"] + d45),   # 45 derece donus
        (p["BAND_R"], p["BAND_Z1"]),                                # sap bandi ustu
        (p["BAND_R"], p["BAND_Z0"]),
        (p["FLANGE_R"], p["BAND_Z0"] - 0.3),
        (p["FLANGE_R"], 1.7), (p["FLANGE_R"] - 0.5, 1.2),          # huni klik yuvasi (V)
        (p["FLANGE_R"], 0.7),
        (p["FLANGE_R"], 0.0),
    ]


def _grooves(p=P):
    """Plakanin iki kenarini tasiyan C kanallar (alt flansin altinda).
    Arka taraf aciktir: plaka oradan disari kayar."""
    hw = p["PLATE_HW"]
    y_in = hw + p["FIT"] / 2                    # kanal ic duvari
    y_out = y_in + p["GROOVE_WALL"]
    z_lip = -(p["PLATE_T"] + p["FIT"] + p["LIP_T"])
    x0, x1 = -p["FLANGE_R"] - 2.0, p["FLANGE_R"] + 2.0
    parts = []
    for s in (1, -1):
        wall = g.extrude(sbox(x0, min(s * y_in, s * y_out), x1, max(s * y_in, s * y_out)),
                         z_lip, 0.5)
        lip = g.extrude(sbox(x0, min(s * (y_in - p["GROOVE_LIP"]), s * y_out), x1,
                             max(s * (y_in - p["GROOVE_LIP"]), s * y_out)),
                        z_lip, z_lip + p["LIP_T"])
        parts += [wall, lip]
    # kapanirken plakayi oturma yuzeyine sikan rampa (dudak ustu one dogru yukselir)
    for s in (1, -1):
        ya, yb = sorted((s * (y_in - p["GROOVE_LIP"]), s * y_in))
        ramp = g.hull(g.extrude(sbox(-p["FLANGE_R"] + p["WEDGE_LEN"], ya, -p["FLANGE_R"] + p["WEDGE_LEN"] + 0.01, yb),
                                z_lip + p["LIP_T"] - 0.01, z_lip + p["LIP_T"]),
                      g.extrude(sbox(-p["FLANGE_R"] - 2.0, ya, -p["FLANGE_R"] - 1.99, yb),
                                z_lip + p["LIP_T"] - 0.01, z_lip + p["LIP_T"] + p["WEDGE"]))
        parts.append(ramp)
    return parts


def build_body(size, p=P):
    h = cup_depth(size, p)
    body = g.revolve(body_profile(size, p))
    # kanallar yalniz flansin altinda: dairesel flans disina tasan kisimlar kesilir
    grooves = g.union(*_grooves(p))
    grooves = g.inter(grooves, g.cyl(p["FLANGE_R"] + 0.01, -10, 1))
    body = g.union(body, grooves)
    # arka: plakanin ve barin gectigi yer (flans arkada acik)
    body = g.diff(body, g.extrude(sbox(p["PLATE_HW"] * 0.0 + 12.0, -(p["PLATE_HW"] + p["FIT"] / 2),
                                       40.0, p["PLATE_HW"] + p["FIT"] / 2),
                                  -(p["PLATE_T"] + p["FIT"] + p["LIP_T"]) - 0.1,
                                  -(p["PLATE_T"] + p["FIT"] + p["LIP_T"]) + p["LIP_T"] + 0.05))
    # O-ring yuvasi: oturma bileziginin alt yuzunde halka kanal
    body = g.diff(body, g.tube(p["ORING_R"] - p["ORING_GW"] / 2, p["ORING_R"] + p["ORING_GW"] / 2,
                               -0.1, p["ORING_GD"]))
    # sap kilit cukurlari
    for i in range(p["SNAP_N"]):
        a = 90.0 + 180.0 * i
        body = g.diff(body, g.sector(p["BAND_R"] - p["SNAP_R"] - 0.4, p["BAND_R"] + 1.0,
                                     a - 11, a + 11, p["BAND_Z0"] + 1.0, p["BAND_Z0"] + 4.6))
    # hazne bosluğu en sonda: hicbir detay olcu hacmine giremez
    top = h + 8.0
    cav = g.revolve([(0.0, 0.0), (p["BORE"] / 2.0, 0.0), (_r_at(h, p), h),
                     (_r_at(top, p), top), (0.0, top)])
    return g.diff(body, cav)


# ===========================================================================
# PARCA 2 -- SURGU  (plaka + bar + uzengi; baski: plaka tablada)
# ===========================================================================
def slider_plan(p=P):
    hw = p["PLATE_HW"]
    circ = Point(0, 0).buffer(hw, resolution=96)
    front = circ.intersection(sbox(-hw - 1, -hw, 0.0, hw))
    back = sbox(0.0, -hw, p["PLATE_BACK"], hw)
    return front.union(back).buffer(0)


def build_slider(p=P, opened=False):
    plate = g.extrude(slider_plan(p), -p["PLATE_T"], 0.0)
    arms, roof = [], None
    for s in (1, -1):
        ya, yb = sorted((s * p["ARM_Y0"], s * p["ARM_Y1"]))
        arms.append(g.extrude(sbox(p["ARM_X0"], ya, p["ARM_X1"], yb), -p["PLATE_T"], p["ARM_TOP"]))
    # 45 derece cati: iki koldan yukselip ortada birlesir (koprü yok)
    cx = (p["ARM_X0"] + p["ARM_X1"]) / 2
    yw = p["ARM_Y1"]
    gable = Polygon([(-yw, 0.0), (yw, 0.0), (0.0, yw)])              # (y, z) ucgen
    gable = gable.intersection(sbox(-yw, 0, yw, p["GABLE_H"]))
    roof = g.extrude(gable, p["ARM_X0"], p["ARM_X1"])
    roof.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    roof.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 0, 1)))
    roof.apply_translation((0, 0, p["ARM_TOP"]))
    # roof simdi: x ARM_X0..X1, y +-yw, z ARM_TOP..ARM_TOP+GABLE_H
    s_ = g.union(plate, *arms, roof)
    if opened:
        s_ = s_.copy(); s_.apply_translation((p["TRAVEL"], 0, 0))
    return s_


# ===========================================================================
# PARCA 3 -- SAP  (ayri, prizmatik, bilezik tablada)
# ===========================================================================
def build_handle(p=P):
    r_i = p["BAND_R"] + p["FIT"] / 2
    r_o = r_i + p["COLLAR_T"]
    z0, z1 = p["BAND_Z0"] - 0.1, p["BAND_Z1"] + 1.4
    collar = g.tube(r_i, r_o, z0, z1)
    # kabin hemen yaninda alcak (ust kapagin etegi buradan gecer), sonra 70 derece rampa ile yukselir
    neck_low = g.extrude(sbox(r_i - 1.0, -p["NECK_HW"], 30.0, p["NECK_HW"]), z0, z1)
    neck_hi = g.hull(g.extrude(sbox(28.5, -p["NECK_HW"], 29.5, p["NECK_HW"]), z0, z1),
                     g.extrude(sbox(34.0, -p["NECK_HW"], p["NECK_X1"], p["NECK_HW"]), z0, p["NECK_TOP"]))
    neck = g.union(neck_low, neck_hi)
    L = p["HANDLE_L"]
    x0, x1 = p["NECK_X1"] - 2.0, p["NECK_X1"] + L
    pts = []
    n = 24
    for i in range(n + 1):
        f = i / n
        w = p["GRIP_HW"] - 3.0 * f ** 1.3
        if f > 0.9:
            w *= np.sqrt(max(0.0, 1 - ((f - 0.9) / 0.1) ** 2)) * 0.85 + 0.15
        pts.append((x0 + f * (x1 - x0), w))
    plan = Polygon(pts + [(x, -y) for x, y in reversed(pts)]).buffer(0)
    grip = g.hull(g.extrude(plan, z0, p["GRIP_TOP"] - 3.5),
                  g.extrude(plan.buffer(-3.0), p["GRIP_TOP"] - 0.9, p["GRIP_TOP"]))
    handle = g.union(collar, neck, grip)
    handle = g.diff(handle, g.cyl(r_i, z0 - 5, p["GRIP_TOP"] + 5))
    for i in range(p["SNAP_N"]):
        a = 90.0 + 180.0 * i
        snap = g.inter(g.revolve([(r_i + 0.6, p["BAND_Z0"] + 1.4), (r_i - p["SNAP_R"], p["BAND_Z0"] + 2.4),
                                  (r_i - p["SNAP_R"], p["BAND_Z0"] + 3.4), (r_i + 0.6, p["BAND_Z0"] + 4.4)]),
                       g.sector(r_i - 3, r_i + 1, a - 9, a + 9, p["BAND_Z0"], p["BAND_Z0"] + 6))
        handle = g.union(handle, snap)
        for sl in (-15.0, 15.0):
            handle = g.diff(handle, g.sector(r_i - 1, r_o + 1, a + sl - 0.7, a + sl + 0.7, z0 - 1, z1 - 1.4))
    return handle


# ===========================================================================
# PARCA 4 -- HUNI (kisa: altta sarkan bir sey yok)
# ===========================================================================
def _thread_ridge(r_crest, r_root, pitch, turns, z0, h_axial, segments=40):
    """Ic dis sirti: kok r_root'tan (etek ici) crest r_crest'e inen, 45 derece
    flankli yamuk kesit, helis boyunca supurulur.  Baskida agiz asagi
    yonunde flanklar 45 derece oldugu icin destek istemez."""
    steps = int(segments * turns)
    rings = []
    depth = r_root - r_crest
    for i in range(steps + 1):
        t = 2 * np.pi * turns * i / steps
        z = z0 + pitch * t / (2 * np.pi)
        ca, sa = np.cos(t), np.sin(t)
        sec = [(r_root + 0.3, -h_axial / 2 - depth), (r_crest, -h_axial / 2),
               (r_crest, h_axial / 2), (r_root + 0.3, h_axial / 2 + depth)]
        rings.append([(r * ca, r * sa, z + dz) for r, dz in sec])
    return g.sweep_rings(rings)


def build_funnel(p=P):
    """Pet siseye VIDALANAN huni.  Alt kismi PCO-1881 kapagi (dis + hava
    yariklari), ust kismi 35 derecelik koni; agzinda kepcenin flansina
    klik diye gecen bilezik.  Sap tarafinda bilezik aciktir (plaka gecer)."""
    z_bot = -(p["PLATE_T"] + p["FIT"] + p["LIP_T"])           # kepcenin alti
    r_m = p["FUN_MOUTH"] / 2
    r_out = p["FUN_OUT_D"] / 2
    wall = 1.8
    tan_c = np.tan(np.radians(p["FUN_CONE_A"]))
    z_cone = z_bot - (r_m - r_out) / tan_c                    # koninin alt ucu = kapak tavani
    r_sk = p["THR_SKIRT_ID"] / 2
    r_ko = r_sk + 2.2                                          # kapak etegi dis yaricapi
    z_cap = z_cone - p["CAP_H"]
    prof = [(r_out, z_cap + 2.0), (r_out, z_cone), (r_m, z_bot),
            (r_m + wall, z_bot), (r_ko, z_cone + 0.0 - (r_m + wall - r_ko) * 0.0),
            (r_ko, z_cap), (r_sk, z_cap), (r_sk, z_cone - 2.0), (r_out, z_cone - 2.0)]
    # basit ve saglam: koni (ic/dis), altina silindirik kapak etegi
    prof = [(r_out, z_cone - 2.0), (r_out, z_cone), (r_m, z_bot), (r_m + wall, z_bot),
            (r_ko, z_cone), (r_ko, z_cap), (r_sk, z_cap), (r_sk, z_cone - 2.0)]
    fun = g.revolve(prof)
    # sise agzinin kapak tavanina yaslandigi 3 ped (aralari hava yolu)
    pads = [g.inter(g.tube(r_out - 0.1, r_sk + 0.1, z_cone - 2.0 - 1.2, z_cone - 2.0),
                    g.sector(0, 20, 120 * i - 20, 120 * i + 20, z_cap, 0))
            for i in range(3)]
    fun = g.union(fun, *pads)
    # dis sirti
    ridge = _thread_ridge(p["THR_CREST_D"] / 2, r_sk, p["THR_PITCH"], p["THR_TURNS"],
                          z_cap + 2.6, p["THR_H"])
    fun = g.union(fun, g.inter(ridge, g.cyl(r_sk + 0.2, z_cap + 0.8, z_cone - 3.0)))
    # hava yariklari (etekte dikey, dis boyunca)
    for i in range(p["VENT_N"]):
        v = g.box(-0.9, 0.9, r_sk - 3.0, r_ko + 1, z_cap - 1, z_cone - 2.6)
        fun = g.diff(fun, g.rotz(v, 360.0 * i / p["VENT_N"] + 45.0))
    # klik bilezik: kepcenin flansini disaridan sarar, ustte boncukla tutar
    r_col = p["FLANGE_R"] + p["FIT"] / 2
    col = g.revolve([(r_col, z_bot), (r_col + wall + 1.4, z_bot), (r_col + wall + 1.4, 2.2),
                     (r_col, 2.2), (r_col, 1.65), (r_col - 0.45, 1.2), (r_col, 0.75)])
    ang = np.degrees(np.arcsin(min(0.99, (p["PLATE_HW"] + 1.0) / r_col)))
    col = g.diff(col, g.sector(0, 40, -ang, ang, z_bot - 1, 3))
    for a in (90.0, 270.0):                                  # esneme yariklari
        for sl in (-14.0, 14.0):
            col = g.diff(col, g.sector(r_col - 1, r_col + 5, a + sl - 0.6, a + sl + 0.6, z_bot - 1, 1.2))
    return g.union(fun, col)


def build_lid(size, p=P):
    """Ust kapak: agzin ustune gecer, boncuga klik yapar; alttaki halka kabin
    icine girip toz sizdirmazligi saglar.  Baski: tepe tablada."""
    h = cup_depth(size, p)
    r_rim_i = _r_at(h, p)
    r_rim_o = r_rim_i + p["WALL"]
    r_sk_i = r_rim_o + p["FIT"] / 2
    r_sk_o = r_sk_i + 2.2
    zt = h + p["LID_T"]                                        # tepe ust yuzu
    zb = h - p["LID_SKIRT"]
    lid = g.revolve([(0.0, h + 0.15), (r_rim_i - p["FIT"] / 2 - p["LID_PLUG"] * 0.0, h + 0.15),
                     (0.0, h + 0.15)][:1] + [
        (0.0, zt), (r_sk_o - 0.6, zt), (r_sk_o, zt - 0.6), (r_sk_o, zb),
        (r_sk_i, zb), (r_sk_i, h + 0.15), (r_rim_i - p["FIT"] / 2, h + 0.15),
        (r_rim_i - p["FIT"] / 2 - 0.4, h - p["LID_PLUG"]),     # sizdirmazlik halkasi (hafif konik)
        (r_rim_i - p["FIT"] / 2 - 1.6, h - p["LID_PLUG"]),
        (r_rim_i - p["FIT"] / 2 - 1.6, h + 0.15), (0.0, h + 0.15)])
    # boncuk yuvasi (45 derece V): etegin icinde
    zc = h - p["LID_BEAD_Z"]
    bd = p["LID_BEAD"] + 0.25
    groove = g.revolve([(r_sk_i - 0.1, zc + 0.15 + bd), (r_sk_i + bd, zc + 0.15),
                        (r_sk_i + bd, zc - 0.15), (r_sk_i - 0.1, zc - 0.15 - bd)])
    lid = g.diff(lid, groove)
    for a in range(0, 360, 90):                                # esneme yariklari
        lid = g.diff(lid, g.sector(r_sk_i - 1, r_sk_o + 1, a + 45 - 0.6, a + 45 + 0.6, zb - 1, zc - 0.6))
    return lid


# ===========================================================================
# PARCA 6 -- TPU CONTA (O-ring bulunmazsa; TPU 95A ile basilir)
# ===========================================================================
def build_gasket(p=P):
    w, hgt = p["ORING_GW"] - 0.15, p["ORING_GD"] + 0.45
    return g.tube(p["ORING_R"] - w / 2, p["ORING_R"] + w / 2, 0.0, hgt)


# ===========================================================================
# DOGRULAMA
# ===========================================================================
def open_fraction(p=P, travel=None):
    bore = Point(0, 0).buffer(p["BORE"] / 2, resolution=128)
    from shapely import affinity
    sh = affinity.translate(slider_plan(p), p["TRAVEL"] if travel is None else travel, 0)
    blocked = bore.intersection(sh).area
    return bore.area - blocked, bore.area
