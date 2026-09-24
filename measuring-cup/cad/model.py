"""Tabani acilan olcu kabi -- parametrik model.

Koordinat sistemi: Z ekseni donme eksenidir, z = 0 duzlemi SIZDIRMAZLIK
KOLTUGUNUN UST kenaridir (bogaz capinin en dar oldugu yer).

Mekanizma: ustteki dugmeye basilinca merkezi mil asagi iner, milin ucundaki
konik "platform" (pistonu) koltuktan ayrilir ve sivi dogrudan pet sise
agzina takili olan boru agizdan bosalir. Birakinca yay platformu tekrar
koltuga oturtur.
"""
import numpy as np
import geom as g
from shapely.geometry import Polygon

# ===========================================================================
# ANA PARAMETRELER  (mm)
# ===========================================================================
P = dict(
    # --- olcu haznesi -----------------------------------------------------
    D_CH        = 34.0,    # hazne ic capi
    WALL        = 2.1,     # cidar (0.42 mm hat x 5 duvar = tam dolu)
    FLOOR_ANGLE = 20.0,    # taban hunisinin egimi (derece)
    FREEBOARD   = 9.0,     # en ust cizgi ile agiz arasi pay (kopru bilezigi
                           # olcek cizgilerini kapatmasin diye)

    # --- valf / koltuk ----------------------------------------------------
    D_THROAT    = 15.0,    # koltugun ust (en dar) capi
    D_SEAT_BOT  = 19.0,    # koltugun alt capi -> 45 derece konik koltuk
    D_PLUG      = 21.0,    # platform capi
    PLUG_LAND   = 2.0,     # platformun silindirik kilavuz bilezigi
    D_GUIDE     = 21.4,    # platformu merkezleyen kilavuz deligi
    Z_GUIDE_BOT = -7.0,    # kilavuz deligi burada biter, altinda genisler
    D_LOW_BORE  = 26.4,    # alt bogaz capi (platform inince akis buradan)
    LIFT        = 5.0,     # dugme stroku = platformun acilma mesafesi
    D_STEM      = 6.0,     # mil capi

    # --- govde etegi / bayonet -------------------------------------------
    D_SKIRT_O   = 36.0,    # base'in gectigi etek dis capi
    Z_BOT       = -16.0,   # govdenin en alt duzlemi
    LUG_N       = 3,
    LUG_H       = 2.0,     # tirnak yuksekligi (eksenel)
    LUG_R       = 1.4,     # tirnak cikintisi (radyal)
    LUG_ARC     = 16.0,    # derece
    LUG_Z       = -12.5,   # tirnak ortasi
    LUG_TWIST   = 30.0,    # kilitleme donusu

    # --- bosaltma agzi (base) --------------------------------------------
    BASE_T      = 4.0,     # bayonet bilezigi et kalinligi
    Z_RING_TOP  = -2.3,
    Z_SHOULDER  = -16.25,  # govdenin oturdugu omuz
    Z_RING_BOT  = -17.6,
    FUNNEL_ANG  = 70.0,    # ic huni (baskida serbest yonde)
    CONE_ANGLE  = 50.0,    # sise agzina oturan merkezleme konisi
    SPOUT_DROP  = 29.0,    # bilezik altindan boru ucuna
    D_SPOUT_O   = 19.0,    # pet sise boynuna giren boru dis capi
    D_SPOUT_TIP = 17.4,    # damlamayi kesen konik uc
    D_SPOUT_I   = 15.0,
    VENT_N      = 4,       # hava tahliye kanali sayisi
    VENT_W      = 3.0,

    # --- altlik / damla tutucu -------------------------------------------
    STAND_WALL  = 2.5,
    STAND_DEPTH = 34.0,    # ic derinlik: boru tabana degerken bilezik tutulur
    STAND_GAP   = 0.6,     # bilezik ile altlik arasi radyal bosluk

    # --- kopru (yoke) + yay ----------------------------------------------
    RING_H      = 7.0,
    RING_T      = 3.4,
    BAR_GAP     = 10.0,    # agiz ile koprunun alti arasi (doldurma bosluğu)
    BAR_T       = 8.0,     # kilavuz deligi boyu
    BAR_W       = 14.0,
    BORE_CL     = 0.35,    # mil - kilavuz deligi capsal bosluğu
    SPR_SEAT_D  = 13.2,
    SPR_SEAT_H  = 1.5,
    SPR_FREE    = 13.0,
    SPR_REST    = 10.0,    # montajda on gerilmeli boy
    SPR_WIRE_R  = 1.4,     # radyal kesit
    SPR_WIRE_Z  = 2.4,     # eksenel kesit
    SPR_MEAN_D  = 10.0,
    SPR_TURNS   = 3.2,
    SNAP_R      = 0.8,     # govde uzerindeki kopru tirnagi cikintisi
    HEAD_D      = 22.0,
    HEAD_T      = 5.0,

    # --- baski toleranslari ----------------------------------------------
    FIT         = 0.25,    # kayan/gecen yuzeyler icin capsal bosluk
    CHAM        = 0.4,     # tabana bakan kenar pahlari
)

SIZES = {15: dict(marks=[5, 10, 15]), 30: dict(marks=[10, 20, 30])}


# ===========================================================================
# HACIM HESABI  (Pappus teoremi -- tam analitik)
# ===========================================================================
def revolve_volume(profile):
    """Kapali (r, z) poligonunun Z etrafinda donmesiyle olusan hacim."""
    p = np.asarray(profile, float)
    r, z = p[:, 0], p[:, 1]
    r2, z2 = np.roll(r, -1), np.roll(z, -1)
    cross = r * z2 - r2 * z
    area = cross.sum() / 2.0
    rc = ((r + r2) * cross).sum() / (6.0 * area)
    return abs(2.0 * np.pi * area * rc)


def liquid_profile(h, p=P):
    """Valf kapaliyken z=h seviyesine kadar olan sivinin (r, z) kesiti."""
    r_th, r_ch = p["D_THROAT"] / 2.0, p["D_CH"] / 2.0
    r_st = p["D_STEM"] / 2.0
    z_floor = (r_ch - r_th) * np.tan(np.radians(p["FLOOR_ANGLE"]))
    z_nose = r_th - r_st                      # 45 derece platform burnu
    return [(r_th, 0.0), (r_ch, z_floor), (r_ch, h), (r_st, h), (r_st, z_nose)]


def fill_height(volume_ml, p=P):
    """Verilen hacmi tam tutturan sivi seviyesini (mm, z=0'dan) cozer."""
    target = volume_ml * 1000.0
    lo, hi = 0.1, 400.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if revolve_volume(liquid_profile(mid, p)) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def geometry_report(p=P):
    rows = []
    for v, cfg in SIZES.items():
        h = fill_height(v, p)
        rows.append(dict(size=v, h_max=h, rim=h + p["FREEBOARD"],
                         marks=[(m, fill_height(m, p)) for m in cfg["marks"]],
                         check=revolve_volume(liquid_profile(h, p)) / 1000.0))
    return rows


# ===========================================================================
# YARDIMCI OLCULER
# ===========================================================================
def dims(p=P):
    d = dict(
        r_ch=p["D_CH"] / 2, r_out=p["D_CH"] / 2 + p["WALL"],
        r_th=p["D_THROAT"] / 2, r_sb=p["D_SEAT_BOT"] / 2,
        r_plug=p["D_PLUG"] / 2, r_guide=p["D_GUIDE"] / 2,
        r_stem=p["D_STEM"] / 2, r_sk=p["D_SKIRT_O"] / 2,
        r_low=p["D_LOW_BORE"] / 2,
    )
    d["z_floor"] = (d["r_ch"] - d["r_th"]) * np.tan(np.radians(p["FLOOR_ANGLE"]))
    d["z_seat_bot"] = -(d["r_sb"] - d["r_th"])          # 45 derece koltuk
    d["z_plug_cone"] = -(d["r_plug"] - d["r_th"])       # 45 derece platform
    d["z_plug_bot"] = d["z_plug_cone"] - p["PLUG_LAND"]
    d["z_nose"] = d["r_th"] - d["r_stem"]
    d["z_bore_flare"] = p["Z_GUIDE_BOT"] - (d["r_low"] - d["r_guide"])  # 45 der.
    return d


def rim_z(size, p=P):
    return fill_height(size, p) + p["FREEBOARD"]


# ===========================================================================
# PARCA 1 -- GOVDE
# ===========================================================================
def body_profile(size, p=P):
    """Govdenin (r, z) kesiti -- hem kati model hem teknik cizim bunu kullanir."""
    d, H, c = dims(p), rim_z(size, p), p["CHAM"]
    return [
        (d["r_low"], p["Z_BOT"] + c),
        (d["r_low"], d["z_bore_flare"]),      # alt bogaz
        (d["r_guide"], p["Z_GUIDE_BOT"]),     # 45 derece daralma
        (d["r_guide"], d["z_seat_bot"]),      # platform kilavuz deligi
        (d["r_sb"], d["z_seat_bot"]),         # koltuk alt kenari
        (d["r_th"], 0.0),                     # koltuk ust kenari  (z = 0)
        (d["r_ch"], d["z_floor"]),            # taban hunisi
        (d["r_ch"], H),                       # hazne ic cidari
        (d["r_out"] - 0.8, H),                # agiz ust yuzeyi
        (d["r_out"], H - 0.8),                # agiz pahi (kopru kilavuzu)
        (d["r_out"], d["z_seat_bot"]),
        (d["r_sk"], d["z_seat_bot"]),         # etege gecis
        (d["r_sk"], p["Z_BOT"] + c),
        (d["r_sk"] - c, p["Z_BOT"]),          # tabana bakan pahlar
        (d["r_low"] + c, p["Z_BOT"]),
    ]


def build_body(size, p=P, marks=True):
    """Olcu haznesi + 45 derece konik sizdirmazlik koltugu + bayonet etek."""
    d, H = dims(p), rim_z(size, p)
    body = g.revolve(body_profile(size, p))
    # --- bayonet tirnaklari (alt yuzey duz: yuk tasir, ust pah: kolay girer)
    lug_prof = [(d["r_sk"] - 0.1, p["LUG_Z"] - p["LUG_H"] / 2),
                (d["r_sk"] + p["LUG_R"], p["LUG_Z"] - p["LUG_H"] / 2),
                (d["r_sk"] + p["LUG_R"], p["LUG_Z"] + p["LUG_H"] / 2 - 0.6),
                (d["r_sk"] + p["LUG_R"] - 0.6, p["LUG_Z"] + p["LUG_H"] / 2),
                (d["r_sk"] - 0.1, p["LUG_Z"] + p["LUG_H"] / 2)]
    lug_ring = g.revolve(lug_prof)
    lugs = [g.inter(lug_ring, g.sector(d["r_sk"] - 1, d["r_sk"] + 5,
                                       360.0 * i / p["LUG_N"] - p["LUG_ARC"] / 2,
                                       360.0 * i / p["LUG_N"] + p["LUG_ARC"] / 2,
                                       p["LUG_Z"] - 3, p["LUG_Z"] + 3))
            for i in range(p["LUG_N"])]
    body = g.union(body, *lugs)

    # --- kopru tirnaklari (2 adet, 90 / 270 derece) -----------------------
    snap_prof = [(d["r_out"] - 0.1, H - 6.2), (d["r_out"] + p["SNAP_R"], H - 5.2),
                 (d["r_out"] + p["SNAP_R"], H - 3.4), (d["r_out"] - 0.1, H - 2.4)]
    snap_ring = g.revolve(snap_prof)
    snaps = [g.inter(snap_ring, g.sector(d["r_out"] - 1, d["r_out"] + 4, a - 10, a + 10,
                                         H - 7, H - 1.5))
             for a in (90.0, 270.0)]
    body = g.union(body, *snaps)

    # --- tutus kanallari ---------------------------------------------------
    ribs = [g.sector(d["r_out"] - 0.5, d["r_out"] + 0.9, a - 2.0, a + 2.0,
                     2.0, H - 8.0)
            for a in (60.0, 78.0, 282.0, 300.0)]
    body = g.union(body, *ribs)

    if marks:
        body = g.union(body, *graduations(size, H, d, p))
    return body


def graduations(size, H, d, p):
    """Dis cidara kabartma olcek cizgileri ve rakamlar."""
    out, r = [], d["r_out"]
    for ml in SIZES[size]["marks"]:
        z = fill_height(ml, p)
        out.append(g.sector(r - 0.5, r + 0.7, -22, 8, z - 0.55, z + 0.55))
        out.append(g.emboss_text(str(ml), 5.0, 0.7, r - 0.15, z, arc_center_deg=26))
    z_max = fill_height(size, p)
    out.append(g.sector(r - 0.5, r + 0.7, -46, -24, z_max - 0.55, z_max + 0.55))
    out.append(g.emboss_text("MAX", 3.2, 0.7, r - 0.15, z_max - 3.6, arc_center_deg=-35))
    out.append(g.emboss_text("%d mL" % size, 6.0, 0.8, r - 0.15, H * 0.42,
                             arc_center_deg=180))
    return out


# ===========================================================================
# PARCA 2 -- PLATFORM + MIL + DUGME  (poppet)
# ===========================================================================
def poppet_profile(size, p=P):
    """Platform + mil + dugme (r, z) kesiti."""
    d, H = dims(p), rim_z(size, p)
    z_hb = H + p["BAR_GAP"] + p["BAR_T"] - p["SPR_SEAT_H"] + p["SPR_REST"]
    r_h = p["HEAD_D"] / 2
    return [
        (0.0, d["z_plug_bot"]),
        (d["r_plug"], d["z_plug_bot"]),            # platformun alt duz yuzu
        (d["r_plug"], d["z_plug_cone"]),           # kilavuz bilezigi
        (d["r_th"], 0.0),                          # 45 derece sizdirmazlik konisi
        (d["r_stem"], d["z_nose"]),                # akisi yonlendiren burun
        (d["r_stem"], z_hb),                       # mil
        (r_h, z_hb),                               # yay oturma yuzeyi
        (r_h, z_hb + p["HEAD_T"] - 0.8),
        (r_h - 0.8, z_hb + p["HEAD_T"]),           # dugme ust pahi
        (0.0, z_hb + p["HEAD_T"]),
    ]


def build_poppet(size, p=P, lowered=False):
    d, H = dims(p), rim_z(size, p)
    z_hb = H + p["BAR_GAP"] + p["BAR_T"] - p["SPR_SEAT_H"] + p["SPR_REST"]
    m = g.revolve(poppet_profile(size, p))
    # dugme yuzeyinde kaymayi onleyen halka kanallar
    for rr in (4.0, 6.5, 9.0):
        m = g.diff(m, g.tube(rr - 0.6, rr + 0.6, z_hb + p["HEAD_T"] - 0.6,
                             z_hb + p["HEAD_T"] + 1))
    if lowered:
        m = g.movez(m, -p["LIFT"])
    return m


# ===========================================================================
# PARCA 3 -- BOSALTMA AGZI (base)
# ===========================================================================
def base_profile(p=P):
    """Bosaltma agzinin (r, z) kesiti."""
    d = dims(p)
    r_i = d["r_sk"] + p["FIT"] / 2
    r_o = r_i + p["BASE_T"]
    r_sp_o, r_sp_i = p["D_SPOUT_O"] / 2, p["D_SPOUT_I"] / 2
    z_fun = p["Z_SHOULDER"] - (r_i - r_sp_i) * np.tan(np.radians(90 - p["FUNNEL_ANG"]))
    z_cone = p["Z_RING_BOT"] - (r_o - r_sp_o) / np.tan(np.radians(p["CONE_ANGLE"]))
    z_tip = p["Z_RING_BOT"] - p["SPOUT_DROP"]
    assert z_cone > z_tip + 3, "boru konisi cok uzun"
    return [
        (r_sp_i, z_tip),
        (r_sp_i, z_fun),                  # boru ic capi
        (r_i, p["Z_SHOULDER"]),           # ic huni
        (r_i, p["Z_RING_TOP"]),           # etegin gectigi silindirik delik
        (r_o, p["Z_RING_TOP"]),
        (r_o, p["Z_RING_BOT"]),           # bayonet bilezigi
        (r_sp_o, z_cone),                 # sise agzi merkezleme konisi
        (r_sp_o, z_tip + 4.0),
        (p["D_SPOUT_TIP"] / 2, z_tip),    # keskin, damlatmayan uc
    ]


def build_base(p=P):
    """Bayonet bilezigi + sise agzina oturan koni + pet sise borusu."""
    d = dims(p)
    r_i = d["r_sk"] + p["FIT"] / 2                 # etegin gectigi delik
    r_o = r_i + p["BASE_T"]
    r_sp_o, r_sp_i = p["D_SPOUT_O"] / 2, p["D_SPOUT_I"] / 2
    z_fun = p["Z_SHOULDER"] - (r_i - r_sp_i) * np.tan(np.radians(90 - p["FUNNEL_ANG"]))
    z_cone = p["Z_RING_BOT"] - (r_o - r_sp_o) / np.tan(np.radians(p["CONE_ANGLE"]))
    z_tip = p["Z_RING_BOT"] - p["SPOUT_DROP"]
    assert z_cone > z_tip + 3, "boru konisi cok uzun"

    base = g.revolve(base_profile(p))

    # --- L seklinde bayonet yuvalari --------------------------------------
    w, cuts = p["LUG_ARC"] + 6.0, []
    z_lo = p["LUG_Z"] - p["LUG_H"] / 2 - 0.25
    z_hi = p["LUG_Z"] + p["LUG_H"] / 2 + 0.25
    r_slot = r_i + p["LUG_R"] + 0.35
    for i in range(p["LUG_N"]):
        a = 360.0 * i / p["LUG_N"]
        cuts.append(g.sector(r_i - 0.5, r_slot, a - w / 2, a + w / 2,
                             p["Z_RING_BOT"] - 1.0, z_hi))          # dikey giris
        cuts.append(g.sector(r_i - 0.5, r_slot, a - w / 2,
                             a + w / 2 + p["LUG_TWIST"] + 9, z_lo, z_hi))  # yatay
    base = g.diff(base, *cuts)

    # kilit sonunda tirnagi tutan kademe ("klik")
    det = [g.sector(r_i - 0.2, r_i + 0.30,
                    360.0 * i / p["LUG_N"] + w / 2 + p["LUG_TWIST"] - 13.0,
                    360.0 * i / p["LUG_N"] + w / 2 + p["LUG_TWIST"] - 8.5,
                    z_lo, p["LUG_Z"] + 0.5)
           for i in range(p["LUG_N"])]
    base = g.union(base, *det)

    # --- hava tahliye kanallari (sise agzi konisi uzerinde) ---------------
    vents = [g.rotz(g.box(-p["VENT_W"] / 2, p["VENT_W"] / 2, r_sp_o + 0.7, r_o + 4,
                          z_cone - 1.0, p["Z_RING_BOT"] + 0.2),
                    360.0 * i / p["VENT_N"] + 45.0)
             for i in range(p["VENT_N"])]
    return g.diff(base, *vents)


# ===========================================================================
# PARCA 4 -- KOPRU (yoke)
# ===========================================================================
def build_yoke(size, p=P):
    """Kaba gecirilen C koprusu: tek koldan destekli, mil kilavuzu + yay yuvasi.

    Tek kol sayesinde kabin on tarafi doldurma icin tamamen aciktir.
    """
    import trimesh
    from shapely.geometry import Polygon, Point

    d, H = dims(p), rim_z(size, p)
    r_i = d["r_out"] + p["FIT"]
    r_o = r_i + p["RING_T"]
    z0, z1 = H - p["RING_H"] + 0.5, H + 0.5
    z_bar0 = H + p["BAR_GAP"]
    z_bar1 = z_bar0 + p["BAR_T"]
    w = p["BAR_W"] / 2

    ring = g.tube(r_i, r_o, z0, z1)

    # --- ucu yuvarlatilmis konsol cubuk (180 dereceden merkeze uzanir) ----
    bar_poly = (Polygon([(-r_o, -w), (2.0, -w), (2.0, w), (-r_o, w)])
                .union(Point(2.0, 0).buffer(w, resolution=32)))
    bar = g.extrude(bar_poly, z_bar0, z_bar1)

    # --- kol: bilezik hizasinda dik, agiz seviyesinin ustunde ice yatik ---
    lo = g.box(-r_o, -(r_i + 0.05), -w, w, z0, z1)
    hi = g.box(-(r_o - 4.6), -(r_o - 12.0), -w, w, z_bar1 - 2.5, z_bar1)
    lean = trimesh.util.concatenate(
        [g.box(-r_o, -(r_i + 0.05), -w, w, z1 - 0.5, z1), hi]).convex_hull
    yoke = g.union(ring, bar, lo, lean)

    # --- mil kilavuz deligi + yay yuvasi ----------------------------------
    yoke = g.diff(yoke,
                  g.cyl(p["D_STEM"] / 2 + p["BORE_CL"] / 2, z_bar0 - 2, z_bar1 + 2),
                  g.cyl(p["SPR_SEAT_D"] / 2, z_bar1 - p["SPR_SEAT_H"], z_bar1 + 1))

    # --- govde tirnaklarinin oturdugu cepler + esneme yariklari -----------
    pockets, slits = [], []
    for a in (90.0, 270.0):
        pockets.append(g.sector(r_i - 0.3, r_i + p["SNAP_R"] + 0.3, a - 13, a + 13,
                                H - 5.7, H - 3.0))
        for sl in (-19.0, 19.0):
            slits.append(g.sector(r_i - 1, r_o + 1, a + sl - 0.7, a + sl + 0.7,
                                  z0 - 1, H - 1.8))
    return g.diff(yoke, *pockets, *slits)


# ===========================================================================
# PARCA 5 -- BASKI YAY  (metal yay kullanilmayacaksa)
# ===========================================================================
def build_spring(p=P, segments=28):
    rm = p["SPR_MEAN_D"] / 2
    wr, wz = p["SPR_WIRE_R"], p["SPR_WIRE_Z"]
    turns, L = p["SPR_TURNS"], p["SPR_FREE"]
    pitch = (L - wz) / turns
    steps = int(segments * turns)
    rings = []
    for i in range(steps + 1):
        t = 2 * np.pi * turns * i / steps
        z = wz / 2 + pitch * t / (2 * np.pi)
        ca, sa = np.cos(t), np.sin(t)
        sec = [(rm - wr / 2, -wz / 2), (rm + wr / 2, -wz / 2),
               (rm + wr / 2, wz / 2), (rm - wr / 2, wz / 2)]
        rings.append([(r * ca, r * sa, z + dz) for r, dz in sec])
    spring = g.sweep_rings(rings)
    # uclari duzlestir: ilk ve son yarim tur duz otursun
    return spring


# ===========================================================================
# MONTAJ
# ===========================================================================
def build_assembly(size, p=P, open_valve=False):
    parts = {
        "body": build_body(size, p),
        "poppet": build_poppet(size, p, lowered=open_valve),
        "base": build_base(p),
        "yoke": build_yoke(size, p),
    }
    return parts


# ===========================================================================
# MONTAJ KONUMLARI + GIRISIM (interference) KONTROLU
# ===========================================================================
def compressed_spring(p=P, length=None):
    """Yayi montaj boyuna sikistirilmis halde gosterir (sadece gorsel)."""
    m = build_spring(p)
    if length:
        m.apply_scale((1.0, 1.0, float(length) / p["SPR_FREE"]))
    return m


def assembled(size, p=P, open_valve=False):
    """Parcalari montaj konumunda dondurur (base bayonetle kilitli)."""
    return dict(
        body=build_body(size, p),
        poppet=build_poppet(size, p, lowered=open_valve),
        base=g.rotz(build_base(p), -p["LUG_TWIST"]),
        yoke=build_yoke(size, p),
        spring=g.movez(compressed_spring(p, p["SPR_REST"] - (p["LIFT"] if open_valve else 0)),
                       rim_z(size, p) + p["BAR_GAP"] + p["BAR_T"] - p["SPR_SEAT_H"]),
    )


def interference(size, p=P, open_valve=False):
    parts = assembled(size, p, open_valve)
    names = list(parts)
    out = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            try:
                v = g.inter(parts[a], parts[b]).volume
            except Exception:
                v = float("nan")
            out["%s|%s" % (a, b)] = v
    return out


# ===========================================================================
# PARCA 6 -- ALTLIK / DAMLA TUTUCU  (opsiyonel)
# ===========================================================================
def build_stand(p=P):
    """Takimi dik tutan ve son damlalari toplayan kucuk kap.

    Ic cap bayonet bilezigini merkezler; boru ucu tabandaki kucuk kuyuya oturur.
    """
    d = dims(p)
    r_i = (d["r_sk"] + p["FIT"] / 2 + p["BASE_T"]) + p["STAND_GAP"]
    r_o = r_i + p["STAND_WALL"]
    z_fl = 2.5                                    # taban kalinligi
    H = p["STAND_DEPTH"] + z_fl
    prof = [
        (0.0, 0.0), (r_o - 0.6, 0.0), (r_o, 0.6),  # tabana bakan pah
        (r_o, H - 0.6), (r_o - 0.6, H),
        (r_i + 0.8, H), (r_i, H - 0.8),            # agiz pahi (kolay girsin)
        (r_i, z_fl + 1.6),                         # damlalari merkeze toplayan
        (0.0, z_fl),                               # hafif konik taban
    ]
    stand = g.revolve(prof)
    # disari tutus kanallari
    ribs = [g.sector(r_o - 0.6, r_o + 1.0, a - 2.5, a + 2.5, 4.0, H - 4.0)
            for a in range(0, 360, 45)]
    return g.union(stand, *ribs)
