#!/usr/bin/env bash
# Bambu X1C icin dilimlenmis .gcode.3mf uretimi (OrcaSlicer CLI, basik ortam).
# Gereksinim: OrcaSlicer AppImage (--appimage-extract ile acilmis), xvfb-run.
#   ORCA=path/to/squashfs-root/AppRun bash cad/slice_x1c.sh
set -e
ORCA=${ORCA:-./squashfs-root/AppRun}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
S=$ROOT/stl/toz-mini/baski; P=$ROOT/x1c/profil; OUT=$ROOT/x1c
for size in 15 30; do
  tmp=$(mktemp -d)
  xvfb-run -a "$ORCA" --load-settings "$P/machine.json;$P/process.json" --load-filaments "$P/filament.json" \
    --arrange 1 --orient 0 --slice 0 --export-3mf kepce-${size}ml.gcode.3mf --outputdir "$tmp" \
    "$S/01-hazne-${size}ml.stl" "$S/02-surgu-${size}ml.stl" "$S/03-ust-kapak-${size}ml.stl"
  python3 "$ROOT/cad/postprocess_3mf.py" "$tmp/kepce-${size}ml.gcode.3mf" \
    "$ROOT/docs/x1c-plate-${size}.png" "$ROOT/docs/x1c-plate-${size}-small.png" "$ROOT/docs/x1c-top-${size}.png" \
    "$OUT/kepce-${size}ml-X1C.gcode.3mf"
  xvfb-run -a "$ORCA" --load-settings "$P/machine.json;$P/process.json" --load-filaments "$P/filament.json" \
    --arrange 1 --orient 0 --export-3mf kepce-${size}ml-proje.3mf --outputdir "$tmp/p" \
    "$S/01-hazne-${size}ml.stl" "$S/02-surgu-${size}ml.stl" "$S/03-ust-kapak-${size}ml.stl" >/dev/null 2>&1 || true
  cp "$tmp/p/kepce-${size}ml-proje.3mf" "$OUT/"
done
