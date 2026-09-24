"""Toz olceginin montaj kesiti (SVG).  Kesitler elle cizilmez: gercek
meshlerden y = 0 duzlemiyle kesilerek alinir, yani cizim modelle her zaman
birebir ayni olur."""
import html

import numpy as np
import trimesh
from shapely.geometry import Polygon

import kinematics as K
import scoop as S

COL = dict(hazne="#c2603a", kapak="#2f8f5b", sap="#7d5aa6", huni="#37699c",
           toz="#d9b88a", sise="#9aa5ad")

# y = 0 duzlemini (x, z) -> (u, v) olarak duzlestiren donusum
TO_2D = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)


def section_polys(mesh, y=0.0, clip=None):
    """y duzlemiyle kesit; istenirse (xmin, xmax) araligina kirpilir."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sec = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        if sec is None:
            return []
        flat, _ = sec.to_planar(to_2D=TO_2D)
    out = []
    for poly in flat.polygons_full:
        if poly.area <= 0.05:
            continue
        if clip is not None:
            from shapely.geometry import box as _b
            poly = poly.intersection(_b(clip[0], -400, clip[1], 400))
            if poly.is_empty:
                continue
        out.extend(list(poly.geoms) if hasattr(poly, "geoms") else [poly])
    return out


class SVG:
    def __init__(self, w, h, scale, cx, cz):
        self.w, self.h, self.s, self.cx, self.cz = w, h, scale, cx, cz
        self.out = []

    def xy(self, x, z):
        return (self.cx + x * self.s, self.cz - z * self.s)

    def poly(self, poly, fill, op=1.0, stroke="#1d1d1f", sw=0.9):
        rings = [poly.exterior] + list(poly.interiors)
        d = ""
        for r in rings:
            pts = list(r.coords)
            d += " ".join(("M" if i == 0 else "L") + "%.2f %.2f" % self.xy(*p)
                          for i, p in enumerate(pts)) + " Z "
        self.out.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                        'stroke-width="%.2f" fill-rule="evenodd" '
                        'stroke-linejoin="round"/>' % (d, fill, op, stroke, sw))

    def text(self, x, y, s, size=12, anchor="start", weight="400", color="#1d1d1f"):
        self.out.append('<text x="%.1f" y="%.1f" font-family="DejaVu Sans, Arial, '
                        'sans-serif" font-size="%d" font-weight="%s" fill="%s" '
                        'text-anchor="%s">%s</text>'
                        % (x, y, size, weight, color, anchor, html.escape(s)))

    def arrow(self, p0, p1, color="#c22", sw=2.4):
        x0, y0 = self.xy(*p0)
        x1, y1 = self.xy(*p1)
        ang = np.arctan2(y1 - y0, x1 - x0)
        a1 = (x1 - 9 * np.cos(ang - 0.4), y1 - 9 * np.sin(ang - 0.4))
        a2 = (x1 - 9 * np.cos(ang + 0.4), y1 - 9 * np.sin(ang + 0.4))
        self.out.append('<path d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f '
                        'L%.1f %.1f" stroke="%s" stroke-width="%.1f" fill="none" '
                        'stroke-linecap="round"/>'
                        % (x0, y0, x1, y1, a1[0], a1[1], x1, y1, a2[0], a2[1],
                           color, sw))


def bottle_neck(c, z_top):
    ri, ro, rt, rs = 10.87, 12.45, 13.7, 16.5
    h = 17.0
    body = [(ri, z_top), (rt, z_top), (rt, z_top - 3), (ro, z_top - 3),
            (ro, z_top - 6), (rt, z_top - 6), (rt, z_top - 9), (ro, z_top - 9),
            (ro, z_top - h + 3), (rs, z_top - h + 3), (rs, z_top - h),
            (ro + 1.5, z_top - h - 4), (ro + 3, z_top - h - 16),
            (ri + 4, z_top - h - 22), (ri, z_top - h - 22)]
    for sgn in (1, -1):
        c.poly(Polygon([(sgn * x, z) for x, z in body]), COL["sise"], 0.5)


def draw(size=15, p=S.P, scale=3.2):
    h = S.cup_depth(size, p)
    body = S.build_body(size, p)
    handle = S.build_handle(p)
    funnel = S.build_funnel(p)
    G = S.funnel_geometry(p)

    W, H = 1480, 520
    CLIP = (-30.0, 62.0)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d">' % (W, H, W, H),
           '<rect width="%d" height="%d" fill="#fbfaf8"/>' % (W, H)]

    for opened, cx, title in ((False, 210, "KAPALI — daldir, doldur, silme"),
                              (True, 620, "AÇIK — tetik sıkılı")):
        c = SVG(360, 620, scale, cx, 250)
        hatch = S.build_hatch(p, opened=opened)
        if opened:
            bottle_neck(c, G["z_throat"] + 17.0)
            for poly in section_polys(funnel, clip=CLIP):
                c.poly(poly, COL["huni"], 0.95)
        else:
            rb, r_rim = p["BORE"] / 2, S._r_at(h, p)
            c.poly(Polygon([(-rb, 0), (rb, 0), (r_rim, h), (-r_rim, h)]),
                   COL["toz"], 0.9, stroke="#b08b56", sw=0.7)
        for poly in section_polys(body, clip=CLIP):
            c.poly(poly, COL["hazne"], 0.96)
        for poly in section_polys(handle, clip=CLIP):
            c.poly(poly, COL["sap"], 0.96)
        for poly in section_polys(hatch, clip=CLIP):
            c.poly(poly, COL["kapak"], 0.98)

        c.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#bbb" '
                     'stroke-width="0.8" stroke-dasharray="5 4"/>'
                     % (c.xy(0, h + 12)[0], c.xy(0, h + 12)[1],
                        c.xy(0, -75)[0], c.xy(0, -75)[1]))
        if opened:
            c.arrow((34.0, -24.0), (34.0, -11.0))          # tetik yukari
            c.arrow((0.0, -6.0), (0.0, -30.0), "#2277cc")  # toz asagi
            c.arrow((-9.0, -6.0), (-9.0, -26.0), "#2277cc")
            c.arrow((9.0, -6.0), (9.0, -26.0), "#2277cc")
        else:
            c.arrow((40.0, 6.0), (40.0, -6.0), "#888", 1.6)
        svg.append("<g>" + "".join(c.out) + "</g>")
        svg.append('<text x="%d" y="30" font-family="DejaVu Sans, Arial" '
                   'font-size="15" font-weight="700" text-anchor="middle">%s</text>'
                   % (cx, html.escape(title)))

    lx = 1080
    rows = [("Hazne", COL["hazne"], "silme dolum = %d mL" % size),
            ("Kapak + tetik", COL["kapak"], "taban komple acilir, %d derece"
             % p["OPEN_DEG"]),
            ("Sap", COL["sap"], "ayri parca, iki boyda ortak"),
            ("Huni", COL["huni"],
             "pet sise icin" if size == 15 else "30 mL normalde shaker'a, hunisiz"),
            ("Toz", COL["toz"], "%.1f - %.1f g" % (size * 0.35, size * 0.55))]
    svg.append('<text x="%d" y="64" font-family="DejaVu Sans, Arial" font-size="15" '
               'font-weight="700">Parçalar</text>' % lx)
    for i, (n, col, note) in enumerate(rows):
        y = 92 + i * 32
        svg.append('<rect x="%d" y="%d" width="16" height="16" rx="3" fill="%s" '
                   'stroke="#1d1d1f" stroke-width="0.8"/>' % (lx, y - 12, col))
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" '
                   'font-size="12.5" font-weight="600">%s</text>' % (lx + 24, y, n))
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" '
                   'font-size="11" fill="#555">%s</text>'
                   % (lx + 24, y + 14, html.escape(note)))

    facts = [
        "Gozenek: Ø%.0f mm, hicbir daralma yok" % p["BORE"],
        "%d derecede gercekten acik: 792 mm² (%%70)" % p["OPEN_DEG"],
        "Hazne derinligi %.1f mm, h/D = %.2f" % (h, h / p["BORE"]),
        "Tetik stroku 17.8 mm",
        "Kapak, tum strok boyunca hicbir parcaya degmiyor",
        "Huni bogazi Ø%.1f mm (PCO-1881 kovani 21.7)" % p["FUN_THROAT_O"],
    ]
    svg.append('<text x="%d" y="268" font-family="DejaVu Sans, Arial" font-size="15" '
               'font-weight="700">Ölçüler</text>' % lx)
    for i, f in enumerate(facts):
        svg.append('<text x="%d" y="%d" font-family="DejaVu Sans, Arial" '
                   'font-size="11.5" fill="#333">• %s</text>'
                   % (lx, 294 + i * 21, html.escape(f)))
    svg.append('<text x="%d" y="436" font-family="DejaVu Sans, Arial" font-size="11" '
               'fill="#777">Kesitler modelden y=0 düzlemiyle alınmıştır.</text>' % lx)
    svg.append("</svg>")
    return "\n".join(svg)


if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w").write(draw(int(sys.argv[2]) if len(sys.argv) > 2 else 15))
