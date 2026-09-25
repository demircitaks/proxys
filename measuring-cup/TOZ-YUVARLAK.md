# Yuvarlak kepçe — 15 mL / 30 mL

Kepçenin olayı yuvarlak olması. Bu versiyonda kapaklar da yuvarlak: altta ve üstte
birer **disk**, sapın kökündeki **tek bir dikey mil** etrafında yana dönüyor. Ray,
kanal, kızak yok. Kapalıyken silüet baştan sona daire + ince sap. Haznenin altı
**hafif huni**: 45°'lik koni, ucu PET şişe ağzına giren Ø20,8 mm'lik kısa boru —
ayrı huni parçası yok, kepçe şişeye kendi oturur.

![Kepçe](docs/yuvarlak-kepce.png)

**Kullanım:** üst diski sapın üstüne doğru çevir → daldır → diski geri çevir: ön
kenarı fazla tozu **süpürür** (silme), son 14°'de tünele girip klik. Şişenin
ağzına oturt (boru boyna girer), alt diski sapın altına doğru çevir → taban açılır,
toz koniden şişeye akar → geri çevir, klik.

---

## 1. Mekanizma

| | |
|---|---|
| **Mil** | Ø4, sapın kökünde, tabandan kapağın üstüne kadar. Alttan sürülür, başı alt diskin içine gömülür, yarıklı ucu üst diskin üstüne klik yapar. İki diski de taşır. |
| **Alt disk** | Ø48, 2,5 mm. Tabandır; kapalıyken O-ring'e (Ø38 × 1,5) oturur. Sapın altına doğru 150° döner. |
| **Üst disk** | Ø(ağız + 2,4), 2,5 mm. Alt yüzü ağız düzleminde. Kapatırken süpürür. Sapın üstüne doğru 150° döner. |
| **Burun** | Gövdenin önünde, tabandan ağza kadar pivot merkezli bir blok (±22°, 5 mm kalın). İki kapağın mandal kanalları buna oyulur; dış yüzü dönüş eksenine eşmerkezli olduğu için kanal duvarı ile parmak arası her açıda sabittir. |
| **Alt mandal** | Alt diskin ön kenarında 14 mm'lik rijit **tırnak** (3,2 mm dışarı taşar). Kapanmanın son 14°'sinde tırnak burundaki **C-kanala** girer; kanalın tabanı (dudak) girişte 0,35 mm alçak, kapalı konumda diskin altına tam oturur → disk **O-ring'e itilir** (O-ring 0,35 taşar, 0,25 sıkışır). |
| **Üst mandal** | Üst kapağın ön kenarından 3,4 mm aşağı sarkan **bacak**, ucunda içe bakan 0,8 mm **ayak**. Ayak burundaki dudağın altına girer; dudağın altı girişte 0,4 mm yüksek, kapalıda ayağa oturur → kapak **ağza çekilir**, kalkamaz. |
| **Çentik (klik)** | Her tırnağın yanından teğet uzanan 10 mm'lik **yay parmağı**, ucunda 0,6 mm'lik 45° yanaklı **tümsek**. Kapalı konumda tümsek kanal dış duvarındaki yuvaya oturur; açarken parmak ~0,45 mm içeri esneyerek geçer (≈1–2 N, açılış için 3–4 N'luk itme; çantada sallanma torkunun >10 katı). Yay parmağın kendisidir — O-ring'e, mile veya diskin eğilmesine bağlı değil. |
| **Huni** | Gövdeyle tek parça. Üst halkası Ø49,2, alt diskin 0,6 mm altında; 45° koni Ø20,8 × 7 mm boruya iner (PCO-1881 iç çap 21,74 → yanda 0,47 mm hava yolu). Alt disk halka ile flanş arasındaki **yarıktan** yana kayar; huni gövdeye +y tarafındaki 110°'lik **kanatla** bağlı — disk öbür yöne (−y, sapın altına) açıldığı için kanat dönüş yolunda değil. |
| **Sap** | Tek parça altıgen çubuk 12 × 8 mm, 86 mm, asma delikli. Üst yüzü ağız düzleminde: üst disk üstünden kayar, alt diskin kulağı altından geçer. |

| Ölçülen | 15 mL | 30 mL |
|---|---|---|
| Alt disk 1°–150° (1° adım), tümseksiz, gövdeyle girişim | 0,000 mm³ | 0,000 mm³ |
| Üst kapak 1°–150°, tümseksiz, gövdeyle girişim | 0,000 mm³ | 0,000 mm³ |
| Diskler arası | 0,000 mm³ | 0,000 mm³ |
| Tümseğin kanal duvarına binmesi (açılışın ilk 10°'si — parmağın esnediği yer) | 1,69 / 2,09 mm³ | 1,69 / 2,09 mm³ |
| Kapalı konumda tümsek yuvasında, tırnak kanalda | 0 | 0 |
| Silme hacim | 15,0000 mL / 12,2 mm | 30,0000 mL / 22,9 mm |

## 2. Parçalar

![Parçalar](docs/yuvarlak-parcalar.png)

| # | Dosya | Baskı yönü |
|---|---|---|
| 1 | `01-hazne-15ml.stl` · `01-hazne-30ml.stl` | **Ağız tablada (ters), huni yukarı.** Ağız ve sapın üst yüzü tabladadır; koni her iki yönde 45°. Destek yok |
| 2 | `02-alt-disk.stl` | Alt yüz tablada; tırnak ve parmak disk düzleminde. Conta yüzü ütülenir. Ortak |
| 3 | `03-ust-disk-15ml.stl` · `-30ml.stl` | Üst yüz tablada; bacak, ayak ve parmak yukarı. Ayağın 1,8 mm'lik çıkıntısı desteksiz basılır |
| 4 | `04-mil-15ml.stl` · `-30ml.stl` | Baş tablada (boy hazneye göre) |
| 5 | `05-conta-tpu.stl` | Opsiyonel: O-ring yoksa TPU 95A |

Hazne ters basılır: ağız, ağız bandı ve sapın üst yüzü aynı düzlemde tablaya
oturur, huni tepede biter. Hazne yüksekliği 15 mL için 36,5 mm, 30 mL için 47,2 mm.
Huninin üst halkasının 2 mm'lik kenarı ve mandal kanallarının tabanları
(3–5 mm) köprü gibi basılır (rapor: %3,2–3,7 çıkıntı, %80'i köprü) — X1C'de
destek istemez.

## 3. Baskı (Bambu X1C, PETG)

Katman 0,16 mm · duvar 4 · dolgu %15 · destek kapalı · brim hazne için açık ·
ironing alt diskin conta yüzü (ağız zaten tablada). Diskler sıkı dönüyorsa `FIT` 0,30 →
0,40; klik çok sertse `BUMP` 0,6 → 0,45, çok gevşekse parmağı kalınlaştırın
(`FINGER_T` / `LEG_T` +0,3).

## 4. Montaj

1. O-ring'i oturma yüzeyindeki yuvaya bastırın.
2. Alt diski gövdenin altına, kulağı sap köküne gelecek şekilde tutun; üst diski
   üste koyun.
3. **Mili alttan** sürün: alt disk → gövde → üst disk. Yarıklı ucu üst diskin
   üstünde klik yapar. Sökmek için ucu iki yandan sıkıp geri itin.
4. Diskleri çevirip kapatın: son 14°'de tırnak kanala girer, rampa diski
   O-ring'e (üst kapağı ağza) çeker, en sonda parmak **klik** yapar. Açmak
   için kapağı yana itin; ilk 10° dirençlidir.

## 5. Dürüst notlar

- **Gram değil hacim**: ±%2 hacim; 15 mL ≈ 5–8 g, 30 mL ≈ 10–17 g. Bir kez tartın.
- **Diskler yana açılır**: alt disk açıkken sapın altında 150°'de durur, şişenin
  yanında sarkar; huni borusu boyna girdiği için kepçe şişeye tutunur.
- **Huni derinliği**: koni + boru hazneyi 21 mm aşağı uzatır; paketin içine
  daldırırken boru en öne girer, sorun olmaz ama hazneyi kabın dibine kadar
  bastırmayın. Shaker'a döküyorsanız boru ağızdan geçer, koni ağzın üstünde durur.
- **O-ring** yılda bir. **Tıklatmayın**, süpürün. FDM, gıda sertifikasız; elde yıkayın.

## 6. Model

`python3 cad/build_round.py` — STL, `docs/toz-yuvarlak-rapor.json`, görseller.
Parametreler `cad/scoop_round.py` (`P`). Tüneller tırnağın gerçek dönüş yolunun
süpürülmesiyle oyulur; çarpışma, çentik profili ve baskı çıkıntıları her üretimde
ölçülür.
