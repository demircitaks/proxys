"""Tabani acilan TOZ olcegi (protein / pre-workout) -- parametrik model.

Koordinatlar: z = 0 duzlemi SIZDIRMAZLIK DUZLEMIdir; kabin tabani, yani
kapagin ust yuzu buradadir ve hacim datumu budur.  +x SAP yonudur.

Mekanizma: kabin tabaninin TAMAMI tek bir kapaktir.  Kapak, gozenegin sap
tarafindaki kenarina teget bir eksende donuyor; kuyrugu sapin altina kivrilip
tetik pedi oluyor.  Pedi parmakla yukari sikinca kapak asagi doner ve toz
tam capta, hicbir daralma gormeden tek parca halinde duser.  Birakinca yay
kapagi duz oturma yuzeyine geri bastirir.

Neden tam cap: daralan duvar olmadan kemer icin dayanak yoktur.  Toz
sutunu kepcede 13-27 mm oldugundan konsolidasyon ~100-190 Pa; bu, 15-25 mm
"kemerlenme sinirinin" olculdugu rejimin bir mertebe altindadir.
"""
import numpy as np
from shapely.geometry import Polygon, Point, box as sbox
from shapely import affinity

import geom as g

# ===========================================================================
# PARAMETRELER (mm)
# ===========================================================================
P = dict(
    # --- olcu haznesi -----------------------------------------------------
    BORE        = 38.0,   # sizdirmazlik duzlemindeki ic cap = bosaltma capi
    DRAFT       = 1.0,    # derece; asagi dogru genisler (dilim duvara surtmesin)
    WALL        = 2.4,
    RIM_CHAM    = 0.6,    # SADECE dis kenar; ic kenar keskin kalir (silme icin)

    # --- oturma yuzeyi / flans / etek ------------------------------------
    LAND        = 2.5,    # duz sizdirmazlik bileziginin genisligi
    FLANGE_R    = 23.5,
    FLANGE_T    = 2.0,
    SKIRT_R_I   = 22.0,   # kapagin cevresini saran etek (alt yuzey duz olsun)
    SKIRT_Z     = -3.3,   # etek alti = kapak alti  -> tek duz taban

    # --- mekanizma govdesi: mentese, kuyruk ve yay KAPALI kutu icinde ------
    HOUSE_X0    = 23.0,
    HOUSE_X1    = 42.0,
    HOUSE_Y     = 15.5,
    HOUSE_Z     = -13.0,  # kutu tabaninin alt yuzu
    HOUSE_WALL  = 1.6,
    BTN_X0      = 27.6,   # tabandaki dugme acikligi (kuyrugun duz alt yuzu)
    BTN_X1      = 36.6,
    BTN_Y       = 11.0,

    # --- kapak + mentese --------------------------------------------------
    HINGE_X     = 24.2,   # mentese ekseni x; z = 0 (sizdirmazlik duzleminde)
                          # Disk kenarinin (21.5) disinda secildi: (a) kapagin
                          # hicbir noktasi donerken oturma yuzeyine dogru
                          # yukselmez, (b) yay bobini diske carpmadan siğar.
    HATCH_R     = 21.5,   # kapak diski (gozenek + 2.5 mm bilezik)
    HATCH_T     = 3.0,
    ARM_Y       = 13.0,   # kuyruk kolunun yari genisligi (= bogum disi)
    KNUCK_Y0    = 3.6,    # bogumlarin ic yuzu; ortada yay bobini icin bosluk
    PIN_D       = 3.0,    # mentese mili (baskili veya 3 mm celik cubuk / M3)
    PIN_LEN     = 37.0,
    CHEEK_Y0    = 13.9,   # mentese yanaklarinin ic yuzu (= kutu duvari)
    CHEEK_T     = 3.9,
    CHEEK_TOP   = 8.0,
    OPEN_DEG    = 65.0,

    # --- tetik (kapakla tek parca) ----------------------------------------
    # Tetik yuzeyi, kuyrugun 45 derecelik alt yuzudur: hem parmaga dogru
    # bakar hem de kapak "sizdirmaz yuz TABLADA" basildiginda destek istemez.
    TAIL_Y      = 10.5,   # kuyrugun (ve dugmenin) yari genisligi
    BTN_Z       = -13.0,  # dugmenin duz alt yuzu = kutu tabaniyla ayni duzlem
    SEAT_X0     = 28.5,   # yay tablasi: kuyruk ustundeki YATAY duzlem
    SEAT_X1     = 35.0,
    SEAT_Z      = -4.8,

    # --- yay: sapin icinde basma yayi, kuyruktaki yatay tablaya basar ------
    SPR_D       = 8.0,    # yay dis capi
    SPR_TOP     = 20.0,   # sap icindeki cep tavani (z)
    SPR_FREE    = 30.0,   # serbest boy


    # --- sap (AYRI PARCA, iki boyda ortak) --------------------------------
    BAND_R      = 23.8,   # kabin uzerindeki kavrama bandi yaricapi
    BAND_Z0     = 2.0,
    BAND_Z1     = 7.5,
    COLLAR_T    = 3.6,    # sapin bilezik et kalinligi
    HANDLE_L    = 84.0,   # bilezik disindan kullanilabilir boy
    HANDLE_W    = 25.0,   # kavrama genisligi (y)
    GRIP_TOP    = 26.0,   # kavramanin ust yuzeyi (z) -> kesit 24 mm yuksek
    SNAP_N      = 2,
    SNAP_R      = 0.9,

    # --- huni (sadece 15 mL / pet sise) -----------------------------------
    FUN_MOUTH   = 60.0,
    FUN_THROAT_O= 20.4,   # PCO-1881/1810 kovanina (21.74) girer
    FUN_THROAT_I= 18.8,
    FUN_TUBE_L  = 15.0,
    FUN_CONE_A  = 35.0,   # dikeyden derece
    FUN_SEAT_N  = 3,      # oturma pedi sayisi -> aralari daimi havalandirma
    FUN_COLLAR  = 5.0,

    # --- toleranslar ------------------------------------------------------
    FIT         = 0.30,   # toz iceren yerlerde bol bosluk
    CHAM        = 0.4,
)

SIZES = (15, 30)


# ===========================================================================
# HACIM: silme (brim) dolumu
# ===========================================================================
def _r_at(z, p=P):
    """Hazne ic yaricapi; z=0'da BORE/2, yukari dogru DRAFT kadar daralir."""
    return p["BORE"] / 2.0 - z * np.tan(np.radians(p["DRAFT"]))


def brim_volume(h, p=P):
    """z=0 ile z=h arasindaki hacim (mm3) -- kesik koni, analitik."""
    rb = p["BORE"] / 2.0
    t = np.tan(np.radians(p["DRAFT"]))
    return np.pi * (rb * rb * h - rb * t * h * h + t * t * h ** 3 / 3.0)


def cup_depth(volume_ml, p=P):
    lo, hi = 0.1, 300.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if brim_volume(mid, p) < volume_ml * 1000.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def report(p=P):
    rows = []
    for v in SIZES:
        h = cup_depth(v, p)
        rows.append(dict(ml=v, depth=h, check=brim_volume(h, p) / 1000.0,
                         hd=h / p["BORE"], rim_d=2 * _r_at(h, p)))
    return rows




# ===========================================================================
# YARDIMCILAR
# ===========================================================================
import trimesh  # noqa: E402


def _rot_y(mesh, deg, origin=(0, 0, 0)):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(deg), (0, 1, 0), origin))
    return m


def hinge_axis(p=P):
    return [p["HINGE_X"], 0.0, 0.0], [0.0, 1.0, 0.0]


def _pin_bore(r, p=P, y0=-40, y1=40):
    """Mentese ekseni boyunca silindir (kesici olarak kullanilir)."""
    c = g.cyl(r, y0, y1)
    c.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, (1, 0, 0)))
    c.apply_translation((p["HINGE_X"], 0.0, 0.0))
    return c


# ===========================================================================
# PARCA 1 -- HAZNE  (baski yonu: OTURMA YUZEYI TABLADA)
# ===========================================================================
def body_profile(size, p=P):
    """Kabin (r, z) kesiti.  z=0 oturma duzlemi; etek kapagin cevresini sarar."""
    h = cup_depth(size, p)
    rb, w = p["BORE"] / 2.0, p["WALL"]
    r_rim = _r_at(h, p)
    return [
        (rb, 0.0),                                   # oturma bileziginin ic kenari
        (r_rim, h),                                  # hazne ic cidari
        (r_rim + w - p["RIM_CHAM"], h),              # agiz duz yuzeyi = silme kenari
        (r_rim + w, h - p["RIM_CHAM"]),              # SADECE dis pah; ic kenar keskin
        (p["BAND_R"], p["BAND_Z1"]),                 # sap bandinin ustu
        (p["BAND_R"], p["BAND_Z0"]),                 # sap bandi
        (p["FLANGE_R"], p["BAND_Z0"] - 0.3),
        (p["FLANGE_R"], p["SKIRT_Z"]),               # etek disi
        (p["SKIRT_R_I"], p["SKIRT_Z"]),              # etek alti (kapak altiyla duz)
        (p["SKIRT_R_I"], 0.0),                       # etek ici (kapaga 0.5 bosluk)
    ]


def _cheeks(p=P, grow=0.0):
    """Mentese yanaklari = mekanizma kutusunun yan duvarlarinin ust uzantisi."""
    out = []
    for s in (1, -1):
        e = grow
        lo, hi = sorted((s * p["CHEEK_Y0"], s * (p["CHEEK_Y0"] + p["CHEEK_T"])))
        lo, hi = lo - e, hi + e
        out.append(g.hull(
            g.extrude(sbox(13.0 - e, lo, 21.0 + e, hi), -e, 1.0),
            g.extrude(sbox(13.0 - e, lo, p["HOUSE_X1"] + e, hi), -e, 1.0),
            g.extrude(sbox(13.0 - e, lo, 21.0 + e, hi),
                      p["CHEEK_TOP"] - 1.0 + e, p["CHEEK_TOP"] + e)))
    return out


def _housing(p=P):
    """Mentese, kuyruk ve yayi saran kapali kutu.  Alt yuzu duzdur ve
    ortasinda kuyrugun duz alt yuzunun oturdugu dugme acikligi vardir."""
    x0, x1, y, z0 = p["HOUSE_X0"], p["HOUSE_X1"], p["HOUSE_Y"], p["HOUSE_Z"]
    t = p["HOUSE_WALL"]
    outer = g.extrude(sbox(x0, -y, x1, y), z0, p["FLANGE_T"])
    inner = g.extrude(sbox(x0 - 5.0, -(y - t), x1 - t, y - t), z0 + t, p["FLANGE_T"] + 1)
    box = g.diff(outer, inner)
    # on duvar: kapagin salinim bolgesinin altinda kalan kisim kapali; kapagin
    # gercekten ihtiyac duydugu kadari hatch_sweep tarafindan sonradan oyulur
    front = g.extrude(sbox(x0, -y, x0 + t, y), z0, p["SKIRT_Z"])
    # yuvarlak etek ile duz kutu arasindaki hilal bosluğu doldur (kapagin
    # kapali konumu ve salinim yolu disinda): alt yuzeyde yarik kalmasin
    fill = g.diff(g.extrude(sbox(17.0, -y, x0 + t, y), p["SKIRT_Z"], p["FLANGE_T"]),
                  g.cyl(p["SKIRT_R_I"], p["SKIRT_Z"] - 0.1, 0.1))
    box = g.union(box, front, fill)
    # taban: dugme acikligi (kuyruk buraya 0.5 mm bosluklu oturur)
    btn = g.extrude(sbox(p["BTN_X0"], -p["BTN_Y"], p["BTN_X1"], p["BTN_Y"]),
                    z0 - 1.0, z0 + t + 0.5)
    # ust: yayin sapa gectigi delik
    xs = (p["SEAT_X0"] + p["SEAT_X1"]) / 2.0
    hole = g.cyl(p["SPR_D"] / 2 + 0.6, -1.0, p["FLANGE_T"] + 1.0)
    hole.apply_translation((xs, 0.0, 0.0))
    return g.diff(box, btn, hole)


def build_body(size, p=P):
    """Baski yonu: AGIZ TABLADA.  Boylece silme kenari birinci katman kadar
    keskin cikar, oturma bilezigi utulenebilir ust yuzey olur ve kutu ile etek
    (z < 0) baskida yukari dogru buyudugu icin destek istemez."""
    h = cup_depth(size, p)
    body = g.revolve(body_profile(size, p))
    body = g.union(body, *_cheeks(p), _housing(p))

    # mentese mili deligi (mil yandan surulur -> tamamen sokulebilir)
    body = g.diff(body, _pin_bore(p["PIN_D"] / 2 + p["FIT"] / 2, p))

    # sap kilitleme cukurlari
    pockets = []
    for i in range(p["SNAP_N"]):
        a = 90.0 + 180.0 * i
        pockets.append(g.sector(p["BAND_R"] - p["SNAP_R"] - 0.4, p["BAND_R"] + 1.0,
                                a - 11, a + 11, p["BAND_Z0"] + 1.0, p["BAND_Z0"] + 5.6))
    body = g.diff(body, *pockets)

    # --- kapagin supurdugu hacmi EN SONDA oy --------------------------------
    body = g.diff(body, hatch_sweep(p))

    # --- olcu hacmini garanti altina al ------------------------------------
    rb, r_rim = p["BORE"] / 2.0, _r_at(h, p)
    top = h + 8.0
    cav = g.revolve([(0.0, 0.0), (rb, 0.0), (r_rim, h),
                     (_r_at(top, p), top), (0.0, top)])
    return g.diff(body, cav)


# ===========================================================================
# PARCA 2 -- KAPAK + TETIK  (tek parca, baski yonu: SIZDIRMAZ YUZ YUKARI)
# ===========================================================================
def _hatch_solid(p=P, grow=0.0):
    e = grow
    disc = g.revolve([(0.0, -p["HATCH_T"] - e),
                      (p["HATCH_R"] + e - p["CHAM"], -p["HATCH_T"] - e),
                      (p["HATCH_R"] + e, -p["HATCH_T"] - e + p["CHAM"]),
                      (p["HATCH_R"] + e, e), (0.0, e)])
    arm = g.extrude(sbox(14.0, -(p["ARM_Y"] + e), 26.0 + e, p["ARM_Y"] + e),
                    -p["HATCH_T"] - e, e)
    # Kuyruk duz bir kamadir: ust ve alt yuzu da ~50 derece oldugu icin kapak
    # hangi yonde basilirsa basilsin desteksizdir.  Alt yuz tetik yuzeyidir.
    # Kuyruk, (x, z) duzleminde acilari tek tek secilmis bir profilin y
    # yonunde uzatilmasidir.  Boylece her yuzun egimi tam kontrol altindadir:
    # ust yuzler 56-62 derece (desteksiz), yay tablasi ise iki ucundan
    # tutturulmus 6.5 mm'lik bir koprüdür.
    bx0, bx1 = p["BTN_X0"] + 0.5, p["BTN_X1"] - 0.5    # dugme, acikliktan 0.5 dar
    tail_poly = Polygon([
        (20.0, 0.0), (26.0, 0.0),
        (p["SEAT_X0"], p["SEAT_Z"]),                # 62 derece
        (p["SEAT_X1"], p["SEAT_Z"]),                # yay tablasi (yatay koprü)
        (bx1, p["BTN_Z"] + 4.0),                    # 77 derece
        (bx1, p["BTN_Z"]),                          # dugmenin arka kenari
        (bx0, p["BTN_Z"]),                          # DUZ dugme yuzu (tabanla ayni)
        (26.0, -p["HATCH_T"]),                      # 80 derece on yuz
        (20.0, -p["HATCH_T"]),
    ])
    if e:
        tail_poly = tail_poly.buffer(e, join_style=2)
    web = g.extrude(tail_poly, -(p["TAIL_Y"] + e), p["TAIL_Y"] + e)
    web.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    return g.union(disc, arm, web)


def build_hatch(p=P, opened=False):
    hatch = _hatch_solid(p)
    # bogum deligi: mil bastan sona gecer; ortadaki bosluk yay bobinine ait
    # Bobin yuvasi diskin kenarindan SONRA baslar: oturma bilezigi kesilmez.
    hatch = g.diff(hatch, _pin_bore(p["PIN_D"] / 2 + p["FIT"] / 2, p),
                   g.extrude(sbox(p["HATCH_R"] + 0.3, -p["KNUCK_Y0"],
                                  p["HINGE_X"] + 10.0, p["KNUCK_Y0"]),
                             -p["HATCH_T"] - 1, 3.0))
    if opened:
        hatch = _rot_y(hatch, -p["OPEN_DEG"], hinge_axis(p)[0])
    return hatch


def hatch_sweep(p=P, clearance=0.45, steps=28, start=1.2):
    """Kapagin acilis boyunca supurdugu hacim (bosluk paylı) -- govdeden oyulur.
    start>0: kapali konum oyulmaz, boylece oturma bilezigi korunur."""
    solid = _hatch_solid(p, grow=clearance)
    ax = hinge_axis(p)[0]
    return g.union(*[_rot_y(solid, -a, ax)
                     for a in np.linspace(start, p["OPEN_DEG"] + 4.0, steps)])


# ===========================================================================
# PARCA 3 -- SAP  (AYRI PARCA, 15/30 mL ORTAK; baski yonu: YAN YATIK)
# ===========================================================================
def _grip_plan(p=P):
    """Sapin PLAN (xy) silueti.  Parca bu duzlemde prizmatiktir: bilezik
    tablada, kavrama dikey duvar olarak yukselir -> hicbir cikinti yoktur."""
    r_o = p["BAND_R"] + p["FIT"] / 2 + p["COLLAR_T"]
    L = p["HANDLE_L"]
    w0, w1 = p["HANDLE_W"] / 2, p["HANDLE_W"] / 2 - 3.5
    x0, x1 = r_o - 6.0, r_o + L
    pts = []
    n = 26
    for i in range(n + 1):                       # ust kenar
        f = i / n
        x = x0 + f * (x1 - x0)
        w = w0 + (w1 - w0) * f ** 1.3
        if f > 0.90:                             # ucu yuvarlat
            w *= np.sqrt(max(0.0, 1.0 - ((f - 0.90) / 0.10) ** 2)) * 0.85 + 0.15
        pts.append((x, w))
    low = [(x, -y) for x, y in reversed(pts)]
    return Polygon(pts + low).buffer(0)


def build_handle(p=P):
    """Kaba gecen bilezik + kavrama.  Baski yonu: BILEZIK TABLADA, hicbir
    yuzey 45 dereceyi asmaz (parca z boyunca prizmatiktir, tepesi pahli)."""
    r_i = p["BAND_R"] + p["FIT"] / 2
    r_o = r_i + p["COLLAR_T"]
    z0 = p["FLANGE_T"] + 0.15                # kutunun ustune oturur
    z1 = p["BAND_Z1"] + 1.6
    z_top = p["GRIP_TOP"]
    collar = g.tube(r_i, r_o, z0, z1)

    plan = _grip_plan(p)
    grip = g.hull(g.extrude(plan, z0, z_top - 3.5),
                  g.extrude(plan.buffer(-3.2), z_top - 0.9, z_top))
    handle = g.union(collar, grip)
    # Kavramanin koku kabin cidarina girmesin: bilezik deliği bastan acilir.
    handle = g.diff(handle, g.cyl(r_i, z0 - 5.0, z_top + 5.0))

    # --- kilitleme tirnaklari + esneme yariklari --------------------------
    snaps, slits = [], []
    for i in range(p["SNAP_N"]):
        a = 90.0 + 180.0 * i
        snaps.append(g.inter(
            g.revolve([(r_i + 0.6, p["BAND_Z0"] + 1.4),
                       (r_i - p["SNAP_R"], p["BAND_Z0"] + 2.4),
                       (r_i - p["SNAP_R"], p["BAND_Z0"] + 4.2),
                       (r_i + 0.6, p["BAND_Z0"] + 5.2)]),
            g.sector(r_i - 3, r_i + 1, a - 9, a + 9,
                     p["BAND_Z0"], p["BAND_Z0"] + 6)))
        for sl in (-15.0, 15.0):
            slits.append(g.sector(r_i - 1, r_o + 1, a + sl - 0.7, a + sl + 0.7,
                                  z0 - 1, z1 - 1.4))
    handle = g.union(handle, *snaps)
    handle = g.diff(handle, *slits)

    # --- yay cebi: kuyruktaki tablanin tam ustunde -----------------------
    x_s = (p["SEAT_X0"] + p["SEAT_X1"]) / 2.0
    pocket = g.cyl(p["SPR_D"] / 2 + 0.45, 0.0, p["SPR_TOP"])
    pocket.apply_translation((x_s, 0.0, 0.0))
    handle = g.diff(handle, pocket)

    # --- govdenin yanaklari/koprusu ve kapagin supurdugu hacim -----------
    return g.diff(handle, hatch_sweep(p, clearance=0.6, start=0.0),
                  *_cheeks(p, grow=0.4))


# ===========================================================================
# PARCA 4 -- HUNI  (sadece 15 mL / pet sise; baski yonu: AGIZ TABLADA)
# ===========================================================================
def swept_radius(p=P, steps=16, zmin=-60.0, dz=1.0):
    """Kapagin supurdugu zarfin her derinlikteki en buyuk yaricapi.

    Sap tarafindaki tetik pedi (x > HINGE_X) haric tutulur; onun icin huninin
    kenarinda ayri bir yarik acilir.  Huni profili bu olcume gore kesilir,
    boylece huni mumkun olan en kisa boyda kalir ve kapak ona hic degmez.
    """
    import kinematics as K
    hatch = _hatch_solid(p, grow=0.8)
    ax = hinge_axis(p)[0]
    pts = []
    for a in np.linspace(0.0, p["OPEN_DEG"], steps):
        v = _rot_y(hatch, -a, ax).vertices
        pts.append(v[v[:, 0] <= p["HINGE_X"]])
    pts = np.vstack(pts)
    r = np.hypot(pts[:, 0], pts[:, 1])
    zs = np.arange(0.0, zmin - dz, -dz)
    out = []
    for z in zs:
        m = (pts[:, 2] <= z + dz) & (pts[:, 2] >= z - dz)
        out.append((float(z), float(r[m].max()) if m.any() else 0.0))
    return out


def funnel_geometry(p=P, margin=1.6):
    """Huninin ic profilini kapagin OLCULEN supurme zarfindan turetir.

    En sig koni baslangicini arar: koni hicbir derinlikte zarfa girmemeli.
    Boylece huni, kapaga hic degmeden mumkun olan en kisa boyda cikar.
    """
    env = swept_radius(p)
    r_ti = p["FUN_THROAT_I"] / 2
    tan_c = np.tan(np.radians(p["FUN_CONE_A"]))
    best = None
    for k, (zs, _) in enumerate(env):
        R = max(r for z, r in env[:k + 1]) + margin
        ok = True
        for z, r in env[k + 1:]:
            if R - (zs - z) * tan_c < r + margin and r > 0:
                ok = False
                break
        if ok:
            best = (zs, R)
            break
    if best is None:
        zs, R = env[-1][0], max(r for _, r in env) + margin
    else:
        zs, R = best
    z_throat = zs - (R - r_ti) / tan_c
    return dict(R=R, z_cone=zs, z_throat=z_throat,
                z_tip=z_throat - p["FUN_TUBE_L"])


def build_funnel(p=P):
    """Pet sise hunisi (15 mL dozu icin)."""
    G = funnel_geometry(p)
    R, zs, z_th, z_tip = G["R"], G["z_cone"], G["z_throat"], G["z_tip"]
    r_to, r_ti = p["FUN_THROAT_O"] / 2, p["FUN_THROAT_I"] / 2
    wall, col = 1.8, p["FUN_COLLAR"]
    prof = [
        (r_ti, z_tip), (r_ti, z_th),          # bogaz ici
        (R, zs), (R, 0.0),                    # koni ve namlu ici
        (R + wall + col, 0.0),                # kepcenin oturdugu bilezik
        (R + wall + col, -3.5), (R + wall, -3.5),
        (R + wall, zs), (r_to, z_th),         # dis koni
        (r_to, z_tip + 2.0), (r_ti + 0.5, z_tip),
    ]
    fun = g.revolve(prof)
    seat_ring = g.revolve([(r_to - 0.1, z_th - 2.6), (r_to + 4.2, z_th + 1.6),
                           (r_to + 4.2, z_th + 2.4), (r_to - 0.1, z_th + 2.4)])
    seats = [g.inter(seat_ring, g.sector(r_to - 1, r_to + 6,
                                         360.0 * i / p["FUN_SEAT_N"] - 24,
                                         360.0 * i / p["FUN_SEAT_N"] + 24,
                                         z_th - 4, z_th + 4))
             for i in range(p["FUN_SEAT_N"])]
    fun = g.union(fun, *seats)
    # tetik pedinin ve kancalarin gectigi yarik + gorus penceresi
    notch = g.sector(R - 3.0, R + wall + col + 2.0, -34, 34, -17.0, 1.0)
    return g.diff(fun, notch)


# ===========================================================================
# PARCA 5 -- MENTESE MILI
# ===========================================================================
def build_pin(p=P):
    """Ø3 mentese mili.  Baskili kullanilabilir; 3 mm celik cubuk veya bir
    M3 vida da birebir gecer."""
    r = p["PIN_D"] / 2
    L = p["PIN_LEN"]
    return g.revolve([(0, 0), (r - 0.4, 0), (r, 0.5), (r, L - 0.5),
                      (r - 0.4, L), (0, L)])


# ===========================================================================
# PARCA 6 -- BASKILI YAY (burulma yayi bulunmazsa)
# ===========================================================================
def build_spring(p=P, segments=28, turns=6.0, wire_r=1.1, wire_z=1.8):
    rm = (p["SPR_D"] - wire_r) / 2.0
    L = p["SPR_FREE"]
    pitch = (L - wire_z) / turns
    steps = int(segments * turns)
    rings = []
    for i in range(steps + 1):
        t = 2 * np.pi * turns * i / steps
        z = wire_z / 2 + pitch * t / (2 * np.pi)
        ca, sa = np.cos(t), np.sin(t)
        sec = [(rm - wire_r / 2, -wire_z / 2), (rm + wire_r / 2, -wire_z / 2),
               (rm + wire_r / 2, wire_z / 2), (rm - wire_r / 2, wire_z / 2)]
        rings.append([(r * ca, r * sa, z + dz) for r, dz in sec])
    return g.sweep_rings(rings)


# ===========================================================================
# MONTAJ
# ===========================================================================
def assembled(size, p=P, opened=False):
    return dict(body=build_body(size, p), hatch=build_hatch(p, opened=opened),
                handle=build_handle(p))
