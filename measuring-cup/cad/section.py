"""Montaj kesiti (SVG) -- mekanizmanin nasil calistigini gosterir."""
import html

import numpy as np
import model as M

COL = dict(body="#c2603a", poppet="#2f8f5b", base="#37699c", yoke="#7d5aa6",
           liquid="#9ed8f5", bottle="#9aa5ad")


def _mirror(prof):
    pts = [(r, z) for r, z in prof]
    return pts + [(-r, z) for r, z in reversed(pts)]


class Canvas:
    def __init__(self, w, h, scale, cx, cz):
        self.w, self.h, self.s, self.cx, self.cz = w, h, scale, cx, cz
        self.out = []

    def xy(self, r, z):
        return (self.cx + r * self.s, self.cz - z * self.s)

    def poly(self, pts, fill, op=1.0, stroke="#1d1d1f", sw=0.9):
        d = " ".join(("M" if i == 0 else "L") + "%.2f %.2f" % self.xy(*p)
                     for i, p in enumerate(pts)) + " Z"
        self.out.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                        'stroke-width="%.2f" stroke-linejoin="round"/>'
                        % (d, fill, op, stroke, sw))

    def rect(self, r0, r1, z0, z1, fill, op=1.0, mirror=True):
        self.poly([(r0, z0), (r1, z0), (r1, z1), (r0, z1)], fill, op)
        if mirror:
            self.poly([(-r0, z0), (-r1, z0), (-r1, z1), (-r0, z1)], fill, op)

    def line(self, p0, p1, color="#1d1d1f", sw=0.8, dash=None):
        x0, y0 = self.xy(*p0)
        x1, y1 = self.xy(*p1)
        self.out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                        'stroke-width="%.2f"%s/>'
                        % (x0, y0, x1, y1, color, sw,
                           ' stroke-dasharray="%s"' % dash if dash else ''))

    def text(self, x, y, s, size=12, anchor="start", color="#1d1d1f", weight="400"):
        self.out.append('<text x="%.1f" y="%.1f" font-family="DejaVu Sans, Arial, '
                        'sans-serif" font-size="%d" font-weight="%s" fill="%s" '
                        'text-anchor="%s">%s</text>' % (x, y, size, weight, color,
                                                        anchor, s))

    def label(self, r, z, dx, dy, s, size=12, anchor="start"):
        x0, y0 = self.xy(r, z)
        self.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" '
                        'stroke-width="0.7"/>' % (x0, y0, x0 + dx, y0 + dy))
        self.out.append('<circle cx="%.1f" cy="%.1f" r="1.7" fill="#555"/>' % (x0, y0))
        self.text(x0 + dx + (3 if anchor == "start" else -3), y0 + dy + 4, s, size,
                  anchor)


def bottle_neck(c, z_top, p=M.P):
    """PCO-1881 (28 mm) pet sise boynunun semasi."""
    ri, ro, rt, rs = 10.87, 12.45, 13.7, 16.5
    h = 17.0
    prof = [(ri, z_top), (ri, z_top - h - 12), (rs, z_top - h - 16),
            (rs, z_top - h - 19)]
    body = [(ri, z_top), (rt, z_top), (rt, z_top - 3), (ro, z_top - 3),
            (ro, z_top - 6), (rt, z_top - 6), (rt, z_top - 9), (ro, z_top - 9),
            (ro, z_top - h + 3), (rs, z_top - h + 3), (rs, z_top - h),
            (ro + 1.5, z_top - h - 4), (ro + 3, z_top - h - 14),
            (ri + 4, z_top - h - 20), (ri, z_top - h - 20)]
    for pts in (body,):
        c.poly(pts, COL["bottle"], 0.55)
        c.poly([(-r, z) for r, z in pts], COL["bottle"], 0.55)


def draw(size=15, p=M.P, scale=4.2):
    d, H = M.dims(p), M.rim_z(size, p)
    body_p = M.body_profile(size, p)
    base_p = M.base_profile(p)
    z_tip = p["Z_RING_BOT"] - p["SPOUT_DROP"]
    top = H + p["BAR_GAP"] + p["BAR_T"] - p["SPR_SEAT_H"] + p["SPR_REST"] + p["HEAD_T"]

    pw, ph = 330, 640
    lx = 760
    W, Hh = 1140, 620
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d">' % (W, Hh, W, Hh),
           '<rect width="%d" height="%d" fill="#fbfaf8"/>' % (W, Hh)]

    for k, (open_valve, cx, title) in enumerate(
            [(False, 190, "KAPALI — ölçülüyor"),
             (True, 560, "AÇIK — düğmeye basılı")]):
        c = Canvas(pw, ph, scale, cx, 70 + top * scale)
        lift = p["LIFT"] if open_valve else 0.0

        if open_valve:
            bottle_neck(c, z_tip + 17.0, p)

        # --- govde + sivi -------------------------------------------------
        if not open_valve:
            zl = M.fill_height(size, p)
            liq = M.liquid_profile(zl, p)
            c.poly(_mirror(liq), COL["liquid"], 0.85, stroke="#4a9ec9", sw=0.7)
        c.poly(_mirror(body_p), COL["body"], 0.95)
        c.poly(_mirror([(r, z) for r, z in base_p]), COL["base"], 0.95)
        c.poly(_mirror([(r, z - lift) for r, z in M.poppet_profile(size, p)]),
               COL["poppet"], 0.98)

        # --- kopru --------------------------------------------------------
        r_i = d["r_out"] + p["FIT"]
        r_o = r_i + p["RING_T"]
        z0, z1 = H - p["RING_H"] + 0.5, H + 0.5
        zb0 = H + p["BAR_GAP"]
        zb1 = zb0 + p["BAR_T"]
        c.rect(r_i, r_o, z0, z1, COL["yoke"], 0.95)
        c.poly([(-r_o, zb0), (9.0, zb0), (9.0, zb1), (-r_o, zb1)], COL["yoke"], 0.95)
        c.poly([(-r_o, z1), (-r_i, z1), (-(r_o - 12.0), zb0), (-r_o, zb0)],
               COL["yoke"], 0.95)

        # --- yay (sematik) --------------------------------------------------
        zs0 = zb1 - p["SPR_SEAT_H"]
        zs1 = zs0 + p["SPR_REST"] - lift
        for sgn in (1, -1):
            pts = []
            n = 7
            for i in range(n + 1):
                t = i / n
                pts.append((sgn * (4.3 + 1.9 * (i % 2)), zs0 + t * (zs1 - zs0)))
            dd = " ".join(("M" if i == 0 else "L") + "%.2f %.2f" % c.xy(*q)
                          for i, q in enumerate(pts))
            c.out.append('<path d="%s" fill="none" stroke="#444" stroke-width="1.6"/>'
                         % dd)

        # --- eksen + baslik -------------------------------------------------
        c.line((0, z_tip - 6), (0, top + 8), "#aaa", 0.7, "5 4")
        svg.append('<g>' + "".join(c.out) + '</g>')
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" font-size="15"'
                   ' font-weight="700" fill="#1d1d1f" text-anchor="middle">%s</text>'
                   % (cx, 36, title))

        # --- oklar -----------------------------------------------------------
        if open_valve:
            ax, ay = c.xy(0, top + 4)
            svg.append('<path d="M%.1f %.1f l0 26 m-6 -10 l6 10 l6 -10" stroke="#c22" '
                       'stroke-width="2.6" fill="none"/>' % (ax, ay - 34))
            for sgn in (1, -1):
                bx, by = c.xy(sgn * 9.0, -13)
                svg.append('<path d="M%.1f %.1f l0 30 m-5 -9 l5 9 l5 -9" stroke="#2277cc"'
                           ' stroke-width="2.2" fill="none"/>' % (bx, by))

    # --- aciklama kutusu ------------------------------------------------------
    rows = [("Govde", COL["body"], "olcu haznesi + 45° konik koltuk"),
            ("Platform + mil", COL["poppet"], "dugmeye basinca %.0f mm iner" % p["LIFT"]),
            ("Bosaltma agzi", COL["base"], "bayonet + pet sise borusu"),
            ("Kopru", COL["yoke"], "mil kilavuzu + yay yuvasi"),
            ("Sivi", COL["liquid"], "%d mL tam dolum" % size)]
    svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" font-size="15" '
               'font-weight="700">Parcalar</text>' % (lx, 70))
    for i, (n, col, note) in enumerate(rows):
        y = 96 + i * 30
        svg.append('<rect x="%d" y="%d" width="16" height="16" rx="3" fill="%s" '
                   'stroke="#1d1d1f" stroke-width="0.8"/>' % (lx, y - 12, col))
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" font-size="12.5"'
                   ' font-weight="600">%s</text>' % (lx + 24, y, n))
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" font-size="11" '
                   'fill="#555">%s</text>' % (lx + 24, y + 14, note))

    facts = [
        "Hazne ic capi: Ø%.0f mm" % p["D_CH"],
        "%d mL dolum yuksekligi: %.1f mm" % (size, M.fill_height(size, p)),
        "Koltuk: Ø%.0f → Ø%.0f, 45° konik" % (p["D_THROAT"], p["D_SEAT_BOT"]),
        "Platform capi: Ø%.0f mm, strok %.0f mm" % (p["D_PLUG"], p["LIFT"]),
        "Bosaltma borusu: Ø%.1f mm (PCO-1881 uyumlu)" % p["D_SPOUT_O"],
        "Acikken akis kesiti: ~85 mm² (30 mL ~0,8 sn)",
        "Toplam yukseklik: %.0f mm" % (top - z_tip),
    ]
    svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" font-size="15" '
               'font-weight="700">Ana ölçüler</text>' % (lx, 285))
    for i, f in enumerate(facts):
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" '
                   'font-size="11.5" fill="#333">• %s</text>' % (lx, 310 + i * 20, f))
    svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" font-size="11" '
               'fill="#777">Kesit — %d mL. 30 mL modeli yalniz hazne '
               'yüksekliği ile ayrılır.</text>' % (lx, 470, size))
    svg.append('</svg>')
    return "\n".join(svg)


if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w").write(draw(int(sys.argv[2]) if len(sys.argv) > 2 else 15))
