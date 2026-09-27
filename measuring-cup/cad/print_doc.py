#!/usr/bin/env python3
"""BASKI-KILAVUZU.pdf: mini kepce icin 3D yazici baski belgesi (Bambu X1C)."""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
H1 = ParagraphStyle("h1", fontName="DVB", fontSize=17, leading=21, spaceAfter=6)
H2 = ParagraphStyle("h2", fontName="DVB", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("b", fontName="DV", fontSize=9.6, leading=13)
S = ParagraphStyle("s", fontName="DV", fontSize=8.4, leading=11, textColor=colors.HexColor("#444"))
C = ParagraphStyle("c", fontName="DV", fontSize=8.6, leading=11)
CB = ParagraphStyle("cb", fontName="DVB", fontSize=8.6, leading=11)


def P(t, st=B):
    return Paragraph(t, st)


def tbl(rows, widths):
    data = [[P(c, CB if i == 0 else C) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e4dc")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def img(name, w):
    from PIL import Image as PI
    path = os.path.join(DOCS, name)
    iw, ih = PI.open(path).size
    return Image(path, width=w, height=w * ih / iw)


def main():
    rep = json.load(open(os.path.join(DOCS, "toz-mini-rapor.json")))
    out = os.path.join(ROOT, "BASKI-KILAVUZU.pdf")
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
                            title="Mini toz kepçesi — baskı kılavuzu", author="proxys / measuring-cup")
    W = A4[0] - 32 * mm
    el = [P("Mini toz kepçesi 15 / 30 mL — 3D baskı kılavuzu (Bambu Lab X1C)", H1),
          P("Üç parça: hazne, tabanının içindeki kanalda kayan deliksiz sürgü, üst kapak. Pim, O-ring, destek yok. "
            "Sapın üstündeki başparmak sürgüsünü 24 mm kendine çekince taban deliği açılır, toz şişeye akar.", B),
          Spacer(1, 6), img("mini-kepce.png", W * 0.5), Spacer(1, 4),
          P("1. Parçalar ve baskı yönü", H2)]
    orient = {"01-hazne-15ml.stl": ("1", "Taban tablada, ağız yukarı — STL bu yönde. Sap tablada."),
              "01-hazne-30ml.stl": ("1", "Aynı."),
              "02-surgu.stl": ("1", "Alt yüzü tablada, başparmak sürgüsü yukarı. İki boy için ortak."),
              "03-ust-kapak-15ml.stl": ("1", "Dış (düz) yüzü tablada, etek yukarı."),
              "03-ust-kapak-30ml.stl": ("1", "Aynı.")}
    rows = [["Dosya", "Adet", "Hacim", "Boyut (mm)", "Yön / not"]]
    for pt in rep["parcalar"]:
        q, note = orient.get(pt["dosya"], ("1", pt["not_"]))
        rows.append([pt["dosya"], q, "%.1f cm³" % pt["hacim_cm3"], " × ".join("%.0f" % x for x in pt["olcu_mm"]), note])
    el += [tbl(rows, [38 * mm, 10 * mm, 16 * mm, 26 * mm, W - 90 * mm]), Spacer(1, 3),
           P("Bir kepçe = hazne + sürgü + üst kapak (istenen boy). İki boy toplam ≈ 35 cm³ PETG (~45 g).", S),
           Spacer(1, 4), img("mini-parcalar.png", W), P("Soldan sağa: hazne, sürgü, üst kapak.", S),
           P("2. Dilimleyici ayarları (Bambu Studio, X1C)", H2)]
    rows = [["Ayar", "Değer", "Neden"],
            ["Malzeme", "PETG", "Sert, yıkanabilir; klik etekleri esner"],
            ["Nozul / katman", "0,4 mm · 0,16 mm", "0,5 mm çentik tümsekleri ve 0,4 mm kapak dudağı için"],
            ["Duvar / üst-alt", "3 duvar · 4 üst · 4 alt", "Sürgü kanalının 1,2 mm alt derisi ve yay parmakları tamamen duvar"],
            ["Dolgu", "%15", "Sap için yeterli"],
            ["Destek", "KAPALI", "45°'den dik yüzey yok; tek köprü haznenin iç tabanı (sürgü kanalı üstünde 28 mm) ve sapın içindeki kol yarığı tavanı (8 mm)"],
            ["Köprüleme", "Varsayılan, fan %100", "Kanal tavanı 28 mm; delik kenarında hafif sarkma olabilir, işlevi etkilemez"],
            ["Brim", "Gerekmez", "Tüm parçaların geniş düz tabanı var"],
            ["Tabla", "Textured PEI 70 °C", "PETG"],
            ["Elephant foot", "0,15 mm", "Kapak etekleri ve taban kapağı tam ölçüde otursun"]]
    el += [tbl(rows, [32 * mm, 40 * mm, W - 72 * mm]),
           P("3. Montaj ve kullanım", H2)]
    for i, t in enumerate([
            "Sürgüyü sapın ucundan, başparmak sürgüsü yukarıda, sapın içindeki kanala sokup öne itin; plaka haznenin altındaki kanala girer, sonunda klik (kapalı).",
            "Sürgüyü geri çekin: 24 mm sonra ikinci klik (açık). Kapalıyken plaka deliği tamamen örter; çantada dökülmez.",
            "Üst kapağı ağza bastırın; kulağından çekip açın.",
            "Dökerken kepçeyi şişe ağzına oturtun (alttaki havşa ağzı ortalar), başparmakla sürgüyü kendinize çekin, tıklatın, ileri itin.",
            "Temizlik: sürgüyü sapın ucundan tamamen çekip çıkarın; elde yıkayın."], 1):
        el.append(P("%d. %s" % (i, t), B))
    el += [Spacer(1, 4), img("mini-30ml-acik.png", W), P("30 mL, sürgü çekilmiş (açık).", S),
           P("4. İnce ayar (cad/scoop_mini.py, P)", H2)]
    rows = [["Belirti", "Değişiklik"],
            ["Sürgü sıkı / takılıyor", "FIT 0,30 → 0,40; kanal tavanı sarkmışsa CH_H 2,35 → 2,6"],
            ["Sürgü gevşek, klik hissedilmiyor", "BUMP 0,5 → 0,6 veya FING_T 2,0 → 2,4"],
            ["Üst kapak takılmıyor / gevşek", "GROOVE_D 0,5 → 0,6 / 0,4"],
            ["Toz delikten geç akıyor", "HOLE_D 21 → 23 (PL_RF 20,5 kalır, HOLE_X −8,5)"]]
    el += [tbl(rows, [70 * mm, W - 70 * mm]), Spacer(1, 4),
           P("Yeniden üretim: <b>python3 cad/build_mini.py</b> → STL'ler <b>stl/toz-mini/</b>; bu belge <b>python3 cad/print_doc.py</b>.", S),
           P("5. Doğrulama (rapordan)", H2)]
    d = rep["dogrulama"]
    rows = [["Ölçüm", "15 mL", "30 mL"],
            ["Sürgü 0–24 mm kayarken hazneyle girişim (tümseksiz)", "%.2f mm³" % d["15 mL"]["surgu_kayma_mm3"], "%.2f mm³" % d["30 mL"]["surgu_kayma_mm3"]],
            ["Yay parmağı tümseklerinin kanal duvarına binmesi (esneme bölgesi)", "%.2f mm³" % d["15 mL"]["centik_esneme_mm3"], "%.2f mm³" % d["30 mL"]["centik_esneme_mm3"]],
            ["Kapalı / açık / üst kapak takılı", "0 / 0 / 0", "0 / 0 / 0"],
            ["Kapalıyken delik örtülü (plaka ∩ delik / delik hacmi)", "%.2f" % d["15 mL"]["kapaliyken_delik_ortusu_oran"], "%.2f" % d["30 mL"]["kapaliyken_delik_ortusu_oran"]],
            ["Açıkken plaka delik üstünde", "%.2f mm³" % d["15 mL"]["acikken_delik_ortusu_mm3"], "%.2f mm³" % d["30 mL"]["acikken_delik_ortusu_mm3"]],
            ["Silme hacim (derinlik)", "%.4f mL (%.1f mm)" % (d["15 mL"]["hacim_ml"], d["15 mL"]["derinlik_mm"]),
             "%.4f mL (%.1f mm)" % (d["30 mL"]["hacim_ml"], d["30 mL"]["derinlik_mm"])]]
    el += [tbl(rows, [W - 70 * mm, 35 * mm, 35 * mm]), Spacer(1, 4),
           P("FDM baskı gıda sertifikalı değildir; elde yıkayın. Kepçe hacim ölçer: 15 mL ≈ 5–8 g, 30 mL ≈ 10–17 g toz — bir kez tartın.", S)]
    doc.build(el)
    print("->", out)


if __name__ == "__main__":
    main()
