# Mini toz kepçesi — 15 mL / 30 mL

Üç parça, pim yok, O-ring yok, ray yok. Hepsi desteksiz basılır.

![Kepçe](docs/mini-kepce.png)

| Parça | Ne yapar |
|---|---|
| **Hazne** | Yuvarlak; üst kısmı 7° konik, altta **45° huni**, en altta **Ø22 açıklık = tabanın tamamı** (düz taban yok). 15 mL için 15,7 mm, 30 mL için 26,9 mm derin (huni hacim aldığı için). Dışı altta 45° pahlı (hafif huni görünümü). Açıklık, haznenin altındaki ince taban levhasının (alt deri + **sürgü kanalı** + üst deri) içinden geçer; en altta 45° havşa (şişe ağzı ortalanır). **Sap ağız hizasında**, cidara bağlı; 58 mm, asma delikli; kökünde sürgü ayağının geçtiği çatal yarığı. |
| **Sürgü** (taban plakası) | Kanalda kayan **deliksiz** plaka + arkaya uzanan kol + haznenin dışında dik yükselen **ayak** + sapın üstünde tırtıklı **başparmak sürgüsü**. Kapalıyken plaka açıklığın altında, yay parmakları kanal duvarındaki yuvaya oturur (klik); sürgüyü **29 mm kendine çek** → açıklık tamamen açılır, ayak çatalın sonuna dayanır; ileri it → klik, kapalı. Ayak boyu hazneye göre (15/30 ayrı). |
| **Üst kapak** | Ağza klik diye geçen düz kapak, kulaklı; eteği sap hizasında kesik (klik 320°'de). |

**Kullanım:** üst kapağı çıkar → daldır, sıyır → kapağı tak. Dökerken: kepçeyi
şişe ağzına oturt (havşa ağzı ortalar), sapı tutan elin başparmağıyla sürgüyü
kendine çek, hafifçe tıklat, sürgüyü ileri it.

![Açık, alttan](docs/mini-acik-alt.png)

## Ölçülen

| | 15 mL | 30 mL |
|---|---|---|
| Sürgü 0–29 mm kayarken hazneyle girişim (tümseksiz) | 0,000 mm³ | 0,000 mm³ |
| Yay parmağı tümseklerinin kanal duvarına binmesi (arada, esneme 0,35 mm) | 2,41 mm³ | 2,41 mm³ |
| Kapalı / açık konumda, üst kapak takılı, kapak–sürgü | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Kapalıyken açıklık plaka ile tam örtülü; açıkken plaka açıklığın üstünde değil | evet / evet | evet / evet |
| İç hacim (ağza kadar, mesh) | 14,997 mL | 29,992 mL |
| Silme hacim | 15,0000 mL | 30,0000 mL |

## Parçalar ve baskı

![Parçalar](docs/mini-parcalar.png)

| Dosya | Baskı yönü |
|---|---|
| `01-hazne-15ml.stl` · `01-hazne-30ml.stl` | **Ağız tablada (ters)**, sap tablada, huni yukarı. İç huni ve dış pah 45° → destek yok |
| `02-surgu-15ml.stl` · `-30ml.stl` | Plaka tablada, ayak dik yukarı |
| `03-ust-kapak-15ml.stl` · `-30ml.stl` | Dış yüzü tablada, etek yukarı |

PETG · 0,16 mm · 3 duvar · %15 dolgu · destek kapalı. Tek köprü: haznenin iç
tabanı sürgü kanalının üstünde 28 mm köprülenir (X1C için sorun değil).
Ayrıntı: `BASKI-KILAVUZU.pdf`. Sürgü sıkıysa `FIT` 0,30 → 0,40; klik zayıfsa
`BUMP` 0,5 → 0,6; huni daha dik istenirse `FUN_A` 45 → 55 (`cad/scoop_mini.py`).

## Montaj

1. Sürgünün ayağını sapın kökündeki çatal yarığına üstten sokun, plakayı
   haznenin altındaki kanala arkadan sürüp öne itin; sonunda klik (kapalı).
2. Sürgüyü geri çekin: ayak çatalın sonuna dayanınca açıklık tamamen açık.
   Üst kapağı bastırın (eteğin kesik tarafı sapa gelir).
3. Temizlik: sürgüyü arkaya çekip ayağı çataldan yukarı çıkarın.

## Notlar

- Hacim ölçer, gram değil: 15 mL ≈ 5–8 g, 30 mL ≈ 10–17 g. Bir kez tartın.
- Açıklık Ø22, huni 45°: toz kendi ağırlığıyla akar, gerekirse tıklatın. Düz
  taban olmadığı için köşede toz kalmaz.
- Plaka ile üst deri arası düz-düz temas (0,3 mm boşluk); toz için yeterli,
  sıvı için değil. Kapalıyken plakada delik yok: çantada dökülmez.
- FDM gıda sertifikasız; elde yıkayın.

`python3 cad/build_mini.py` → STL (`stl/toz-mini/`), rapor, görseller.
