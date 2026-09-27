# Mini toz kepçesi — 15 mL / 30 mL

Üç parça, pim yok, O-ring yok, ray yok. Hepsi desteksiz basılır.

![Kepçe](docs/mini-kepce.png)

| Parça | Ne yapar |
|---|---|
| **Hazne** | Yuvarlak, Ø38 taban, 7° konik; 15 mL için 12,2 mm, 30 mL için 22,9 mm derin. Tabanı üç katlı: alt deri + **sürgü kanalı** + iç taban; iki deride de öne yakın **Ø21 delik** (alttaki 45° havşalı → şişe ağzı ortalanır). Kanal cidarın dibinden geçip sapın içine devam eder; sapın üstünde sürgü yarığı. 55 mm sap (asma delikli). |
| **Sürgü** (taban plakası) | Kanalda kayan **deliksiz** plaka + sapın içinden geçen kol + sapın üstünden çıkan tırtıklı **başparmak sürgüsü**. Kapalıyken plaka deliğin altında; sürgüyü **24 mm kendine çek** → delik açılır, toz şişeye; ileri it → kapalı. Plakanın iki yanındaki yay parmakları kanal duvarındaki yuvalara iki konumda oturur (klik). İki boy için ortak. |
| **Üst kapak** | Ağza klik diye geçen düz kapak, kulaklı (saklama). |

**Kullanım:** üst kapağı çıkar → daldır, sıyır → kapağı tak. Dökerken: kepçeyi
şişe ağzına oturt (havşa ağzı ortalar), sapı tutan elin başparmağıyla sürgüyü
kendine çek, hafifçe tıklat, sürgüyü ileri it.

![Açık, alttan](docs/mini-acik-alt.png)

## Ölçülen

| | 15 mL | 30 mL |
|---|---|---|
| Sürgü 0–24 mm kayarken hazneyle girişim (tümseksiz) | 0,000 mm³ | 0,000 mm³ |
| Yay parmağı tümseklerinin kanal duvarına binmesi (arada, esneme 0,35 mm) | 2,29 mm³ | 2,29 mm³ |
| Kapalı / açık konumda, üst kapak takılı | 0 / 0 / 0 | 0 / 0 / 0 |
| Kapalıyken delik plaka ile tam örtülü; açıkken plaka deliğin üstünde değil | evet / evet | evet / evet |
| Silme hacim | 15,0000 mL | 30,0000 mL |

## Parçalar ve baskı

![Parçalar](docs/mini-parcalar.png)

| Dosya | Baskı yönü |
|---|---|
| `01-hazne-15ml.stl` · `01-hazne-30ml.stl` | Taban tablada, ağız yukarı; sap tablada. Destek yok |
| `02-surgu.stl` | Alt yüzü tablada, başparmak sürgüsü yukarı. Ortak |
| `03-ust-kapak-15ml.stl` · `-30ml.stl` | Dış yüzü tablada, etek yukarı |

PETG · 0,16 mm · 3 duvar · %15 dolgu · destek kapalı. Tek köprü: haznenin iç
tabanı sürgü kanalının üstünde 28 mm köprülenir (X1C için sorun değil).
Ayrıntı: `BASKI-KILAVUZU.pdf`. Sürgü sıkıysa `FIT` 0,30 → 0,40; klik zayıfsa
`BUMP` 0,5 → 0,6 (`cad/scoop_mini.py`).

## Montaj

1. Sürgüyü sapın ucundan, başparmak sürgüsü yukarıda, kanala sokup öne itin;
   plaka haznenin altındaki kanala girer, sonunda klik (kapalı).
2. Sürgüyü geri çekip ikinci kliği (açık) hissedin. Üst kapağı bastırın.
3. Temizlik: sürgüyü sapın ucundan tamamen çekip çıkarın.

## Notlar

- Hacim ölçer, gram değil: 15 mL ≈ 5–8 g, 30 mL ≈ 10–17 g. Bir kez tartın.
- Taban deliği Ø21: protein tozu için yeterli, sıkışırsa tıklatın. Delik öne
  yakın olduğu için dökerken kepçeyi öne hafif eğin.
- Plaka ile iç taban arası düz-düz temas (0,25 mm boşluk); toz için yeterli,
  sıvı için değil. Kapalıyken plakada delik yok: çantada dökülmez.
- FDM gıda sertifikasız; elde yıkayın.

`python3 cad/build_mini.py` → STL (`stl/toz-mini/`), rapor, görseller.
