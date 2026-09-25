#!/usr/bin/env python3
"""BASKI-KILAVUZU.pdf: 3D yazici icin baski belgesi (Bambu X1C)."""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak)
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


def tbl(rows, widths, head=True):
    data = [[P(c, CB if (head and i == 0) else C) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e4dc")))
    t.setStyle(TableStyle(st))
    return t


def img(name, w):
    from PIL import Image as PI
    path = os.path.join(DOCS, name)
    iw, ih = PI.open(path).size
    return Image(path, width=w, height=w * ih / iw)


def main():
    rep = json.load(open(os.path.join(DOCS, "toz-yuvarlak-rapor.json")))
    parts = rep["parcalar"]
    out = os.path.join(ROOT, "BASKI-KILAVUZU.pdf")
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm,
                            title="Toz kepçesi — baskı kılavuzu", author="proxys / measuring-cup")
    W = A4[0] - 32 * mm
    el = []
    el.append(P("Toz kepçesi 15 / 30 mL — 3D baskı kılavuzu (Bambu Lab X1C)", H1))
    el.append(P("Yuvarlak hazne, döner üst kapak, sapa doğru kayan taban plakası, altta PET şişe ağzına giren huni. "
                "Bu belge yalnız baskı ve montaj içindir; tasarım ayrıntıları için <b>TOZ-YUVARLAK.md</b>.", B))
    el.append(Spacer(1, 6))
    el.append(img("yuvarlak-kepce.png", W * 0.55))
    el.append(Spacer(1, 4))

    el.append(P("1. Parçalar ve baskı yönü", H2))
    orient = {
        "01-hazne-15ml.stl": ("1", "PETG", "Ağız (üst yüz) tablada, huni yukarı — STL zaten bu yönde. Brim açık."),
        "01-hazne-30ml.stl": ("1", "PETG", "Aynı: ağız tablada, huni yukarı. Brim açık."),
        "02-alt-plaka.stl": ("1", "PETG", "Conta yüzü (düz, geniş yüz) tablada; tetik çubuğu ve tümsekler yukarı. İki boy için ortak."),
        "03-ust-disk-15ml.stl": ("1", "PETG", "Üst yüz tablada; bacak, ayak ve yay parmağı yukarı."),
        "03-ust-disk-30ml.stl": ("1", "PETG", "Aynı."),
        "04-mil-15ml.stl": ("1", "PETG", "Baş tablada, dik. Boy hazneye göre (15 → 19,8 mm, 30 → 30,5 mm)."),
        "04-mil-30ml.stl": ("1", "PETG", "Aynı."),
        "05-conta-tpu.stl": ("0–1", "TPU 95A", "Opsiyonel: Ø38×1,5 O-ring yoksa. Düz."),
    }
    rows = [["Dosya", "Adet", "Malzeme", "Hacim", "Boyut (mm)", "Yön / not"]]
    for pt in parts:
        q, mat, note = orient.get(pt["dosya"], ("1", "PETG", pt["not_"]))
        rows.append([pt["dosya"], q, mat, "%.1f cm³" % pt["hacim_cm3"],
                     " × ".join("%.0f" % x for x in pt["olcu_mm"]), note])
    el.append(tbl(rows, [40 * mm, 10 * mm, 16 * mm, 16 * mm, 24 * mm, W - 106 * mm]))
    el.append(Spacer(1, 4))
    el.append(P("Bir kepçe için: hazne + plaka + üst disk + mil (istenen boy) + Ø38×1,5 NBR/silikon O-ring (ya da TPU conta). "
                "Her iki boy için toplam ≈ 75 cm³ PETG (~95 g).", S))
    el.append(Spacer(1, 4))
    el.append(img("yuvarlak-parcalar.png", W))
    el.append(P("Soldan sağa: hazne, taban plakası, üst disk, mil.", S))

    el.append(P("2. Dilimleyici ayarları (Bambu Studio, X1C)", H2))
    rows = [["Ayar", "Değer", "Neden"],
            ["Malzeme", "PETG (Bambu PETG-HF / Basic)", "Sert, gıdayla temasta PLA'dan dayanıklı, yıkanabilir"],
            ["Nozul / katman", "0,4 mm · 0,16 mm", "Yay parmakları ve 0,5 mm tümsekler için ince katman"],
            ["Duvar / üst-alt", "4 duvar · 5 üst · 4 alt", "Raylar, dudaklar ve parmaklar tamamen duvar olsun"],
            ["Dolgu", "%15 gyroid", "Sap ve burun için yeterli"],
            ["Destek", "KAPALI", "Hiçbir parçada 45°'den dik çıkıntı yok; köprüler ≤ 22 mm"],
            ["Brim", "Hazne için 5 mm", "Ters baskıda ağız halkası ve köprü bacakları tablada; devrilmesin"],
            ["Köprüleme", "Varsayılan, fan %100", "Ray üst kenarları 19/22 mm, dudak altları 3–5 mm köprülenir"],
            ["Ironing", "Gerekmez", "Conta yüzü tablada basıldığı için düz"],
            ["Hız", "Varsayılan; ilk katman yavaş", "Yay parmakları 1,6 mm — dış duvar hızı ≤ 120 mm/s"],
            ["Tabla", "Textured PEI, 70 °C", "PETG için yapışkan/ayırıcı gerekmez"],
            ["Elephant foot", "0,15 mm", "Plaka ve disklerin tabla yüzü kenarları şişmesin"]]
    el.append(tbl(rows, [32 * mm, 52 * mm, W - 84 * mm]))

    el.append(P("3. Hazne — neden ters basılıyor", H2))
    el.append(P("Hazne ağzı, ağızdaki burun, sapın üst yüzü ve köprü bacakları aynı düzlemde tablaya oturur; "
                "huni yukarıda biter. Huninin konisi ve rayların dudakları her iki yönde 45° olduğundan destek istemez. "
                "Tabladan ayırırken huni borusundan değil ağız kenarından tutun.", B))
    el.append(Spacer(1, 4))
    el.append(img("yuvarlak-15ml-kapali.png", W))
    el.append(P("15 mL, kapalı. Görseller model koordinatında (ağız yukarı); baskıda 180° ters.", S))

    el.append(PageBreak())
    el.append(P("4. Montaj", H2))
    steps = ["O-ring'i haznenin alt yüzündeki yuvaya bastırın (yuvadan 0,35 mm taşar).",
             "Mili alttan göbeğe sürün, üst diski takın; yarıklı uç diskin üstünde klik yapar. Sökmek için ucu iki yandan sıkıp geri itin.",
             "Taban plakasını arkadan, tetik aşağıda, raylara sürün: pahlı kenarlar dudaklara oturur. İlk klik açık konum, ikincisi kapalı. "
             "Plaka mil başını da kapattığı için mil düşmez.",
             "Kontrol: plaka 42 mm'lik yolda takılmadan kaymalı, iki uçta klik vermeli; üst disk 120° dönüp son 14°'de burna girmeli."]
    for i, t in enumerate(steps, 1):
        el.append(P("%d. %s" % (i, t), B))
    el.append(Spacer(1, 4))
    el.append(img("yuvarlak-30ml-acik.png", W))
    el.append(P("30 mL, açık: plaka sapa doğru 42 mm kaymış, üst disk 120° açık.", S))

    el.append(P("5. İlk baskıdan sonra ince ayar", H2))
    rows = [["Belirti", "Değişiklik (cad/scoop_round.py, P)"],
            ["Plaka sıkı / sürtüyor", "FIT 0,30 → 0,40 (tüm boşluklar)"],
            ["Plaka gevşek, klik hissedilmiyor", "PFING_T 1,6 → 2,0 (parmak kalınlığı) veya PBUMP 0,5 → 0,6"],
            ["Klik çok sert", "PBUMP 0,5 → 0,4; üst kapak için BUMP 0,6 → 0,45"],
            ["Üst disk burna girmiyor", "LEG_H 3,4 → 3,3 veya FIT +0,05"],
            ["Huni şişe ağzına girmiyor", "SPOUT_D 20,8 → 20,5 (PCO-1881 iç çap 21,74)"],
            ["Hacim sapması", "cup_depth hesabı DRAFT/BORE'a bağlı; tartıp WALL değil BORE'u düzeltin"]]
    el.append(tbl(rows, [60 * mm, W - 60 * mm]))
    el.append(Spacer(1, 4))
    el.append(P("Yeniden üretim: <b>python3 cad/build_round.py</b> → STL'ler <b>stl/toz-yuvarlak/</b>, rapor "
                "<b>docs/toz-yuvarlak-rapor.json</b>, bu belge <b>python3 cad/print_doc.py</b>.", S))

    el.append(P("6. Doğrulama özeti (rapordan)", H2))
    d = rep["dogrulama"]
    rows = [["Ölçüm", "15 mL", "30 mL"]]
    keys = [("plaka_kayma_mm3", "Plaka 0–50 mm kayarken gövdeyle girişim (tümseksiz)"),
            ("ust_kapak_donus_mm3", "Üst kapak 1–120° gövdeyle girişim (tümseksiz)"),
            ("plaka_tumsek_girisim_mm3", "Plaka tümseklerinin raya binmesi (esneme bölgesi)"),
            ("ust_tumsek_girisim_mm3", "Kapak tümseğinin kanal duvarına binmesi (ilk 10°)"),
            ("kapali_plaka_mm3", "Kapalı konum (tümsek yuvada)"), ("acik_plaka_mm3", "Açık konum (tümsek yuvada)")]
    for k, lab in keys:
        rows.append([lab, "%.2f mm³" % d["15 mL"][k], "%.2f mm³" % d["30 mL"][k]])
    for k in d["kalibrasyon"]:
        rows.append(["Silme hacim %d mL → derinlik" % k["ml"], "%.2f mm" % k["derinlik_mm"], "%.4f mL" % k["olculen_ml"]])
    el.append(tbl(rows, [W - 60 * mm, 30 * mm, 30 * mm]))
    el.append(Spacer(1, 4))
    el.append(P("Uyarı: FDM baskı gıda sertifikalı değildir; elde yıkayın, bulaşık makinesine koymayın. "
                "Kepçe hacim ölçer, gram değil: 15 mL ≈ 5–8 g, 30 mL ≈ 10–17 g toz — bir kez tartın.", S))
    doc.build(el)
    print("->", out)


if __name__ == "__main__":
    main()
