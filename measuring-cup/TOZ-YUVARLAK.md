# Yuvarlak kepçe — 15 mL / 30 mL

Kepçenin olayı yuvarlak olması. Bu versiyonda kapaklar da yuvarlak: altta ve üstte
birer **disk**, sapın kökündeki **tek bir dikey mil** etrafında yana dönüyor. Ray,
kanal, kızak yok. Kapalıyken silüet baştan sona daire + ince sap.

![Kepçe](docs/yuvarlak-kepce.png)

**Kullanım:** üst diski sapın üstüne doğru çevir → daldır → diski geri çevir: ön
kenarı fazla tozu **süpürür** (silme), son 14°'de tünele girip klik. Şişenin
üstünde alt diski sapın altına doğru çevir → taban açılır → geri çevir, klik.

---

## 1. Mekanizma

| | |
|---|---|
| **Mil** | Ø4, sapın kökünde, tabandan kapağın üstüne kadar. Alttan sürülür, başı alt diskin içine gömülür, yarıklı ucu üst diskin üstüne klik yapar. İki diski de taşır. |
| **Alt disk** | Ø48, 2,5 mm. Tabandır; kapalıyken O-ring'e (Ø38 × 1,5) oturur. Sapın altına doğru 150° döner. |
| **Üst disk** | Ø(ağız + 2,4), 2,5 mm. Alt yüzü ağız düzleminde. Kapatırken süpürür. Sapın üstüne doğru 150° döner. |
| **Teğet kilit** | Her diskin ön kenarında 14 mm'lik bir tırnak var. Kapanmanın son 14°'sinde tırnak, gövdenin önündeki **tünele** yandan girer. Tünelin tavanı 0,45 mm alçalır → disk O-ring'e sıkışır (üst disk için ağza bastırılır). |
| **Çentik** | Tünelin ucunda 0,35 mm'lik tümsek. Disk geçerken O-ring esner, geçince kama tekrar sıkar → **klik**, çantada açılmaz. Yay yok: O-ring'in kendisi yay. |
| **Sap** | Tek parça altıgen çubuk 12 × 8 mm, 86 mm, asma delikli. Alt diskin kulağı altından, üst disk üstünden geçer. |

| Ölçülen | 15 mL | 30 mL |
|---|---|---|
| Alt disk 3°–150° dönüşte gövdeyle girişim (yalnız çentik tümseği, 0,35 mm) | 0,40 mm³ | 0,40 mm³ |
| Üst disk 3°–150° dönüşte gövdeyle girişim (yalnız çentik) | 0,40 mm³ | 0,39 mm³ |
| Alt disk – huni bileziği, diskler arası | 0,000 mm³ | 0,000 mm³ |
| Huni bileziği – gövde (takılı) | 0,000 mm³ | 0,000 mm³ |
| Kapalıyken tırnak–tünel girişimi | 0 (kama sadece O-ring'i sıkar) | 0 |
| Silme hacim | 15,0000 mL / 12,2 mm | 30,0000 mL / 22,9 mm |

## 2. Parçalar

![Parçalar](docs/yuvarlak-parcalar.png)

| # | Dosya | Baskı yönü |
|---|---|---|
| 1 | `01-hazne-15ml.stl` · `01-hazne-30ml.stl` | **Ağız yukarı, oturma yüzü tablada** — tam düz. Sap dahil, destek yok |
| 2 | `02-alt-disk.stl` | Alt yüz tablada, tırnak yukarı. Conta yüzü ütülenir. Ortak |
| 3 | `03-ust-disk-15ml.stl` · `-30ml.stl` | Üst yüz tablada, tırnak yukarı |
| 4 | `04-mil-15ml.stl` · `-30ml.stl` | Baş tablada (boy hazneye göre) |
| 5 | `05-huni-pet-vidali.stl` | Opsiyonel: bileziği alt diskin dönüş yolundan oyulmuş (önde beşik) |
| 6 | `06-conta-tpu.stl` | Opsiyonel: O-ring yoksa TPU 95A |

Sap artık gövdeyle tek parça ve tabladan **0,5 mm** yukarıda başlar: ilk katman
tablaya yapışır, payanda gerekmez. Hiçbir parça destek istemez.

## 3. Baskı (Bambu X1C, PETG)

Katman 0,16 mm · duvar 4 · dolgu %15 · destek kapalı · brim hazne için açık ·
ironing hazne ağzı ve alt diskin conta yüzü. Diskler sıkı dönüyorsa `FIT` 0,30 →
0,40; tırnak tünele girmiyorsa `TAB_H`'yi 0,1 azaltın.

## 4. Montaj

1. O-ring'i oturma yüzeyindeki yuvaya bastırın.
2. Alt diski gövdenin altına, kulağı sap köküne gelecek şekilde tutun; üst diski
   üste koyun.
3. **Mili alttan** sürün: alt disk → gövde → üst disk. Yarıklı ucu üst diskin
   üstünde klik yapar. Sökmek için ucu iki yandan sıkıp geri itin.
4. Diskleri çevirip kapatın: tırnaklar tünele girer, son derecelerde direnç ve klik.

## 5. Dürüst notlar

- **Gram değil hacim**: ±%2 hacim; 15 mL ≈ 5–8 g, 30 mL ≈ 10–17 g. Bir kez tartın.
- **Diskler yana açılır**: alt disk açıkken sapın altında 150°'de durur; şişe
  ağzının üstünde yer ister — huni kullanıyorsanız bileziği bu yüzden önde beşik.
- **O-ring** yılda bir. **Tıklatmayın**, süpürün. FDM, gıda sertifikasız; elde yıkayın.

## 6. Model

`python3 cad/build_round.py` — STL, `docs/toz-yuvarlak-rapor.json`, görseller.
Parametreler `cad/scoop_round.py` (`P`). Tüneller tırnağın gerçek dönüş yolunun
süpürülmesiyle oyulur; çarpışma, çentik profili ve baskı çıkıntıları her üretimde
ölçülür.
