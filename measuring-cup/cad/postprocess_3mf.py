#!/usr/bin/env python3
"""Orca CLI'nin urettigi .gcode.3mf'e: onizleme PNG'leri, X1C model kimligi, png content-type."""
import sys, zipfile, re, shutil
src, png512, png128, pngtop, out = sys.argv[1:6]
zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED)
names = zin.namelist()
for n in names:
    data = zin.read(n)
    if n == "[Content_Types].xml":
        s = data.decode()
        if 'Extension="png"' not in s:
            s = s.replace("</Types>", ' <Default Extension="png" ContentType="image/png"/>\n</Types>')
        data = s.encode()
    elif n == "Metadata/slice_info.config":
        s = data.decode()
        s = s.replace('key="printer_model_id" value=""', 'key="printer_model_id" value="BL-P001"')
        s = s.replace('key="X-BBL-Client-Version" value=""', 'key="X-BBL-Client-Version" value="01.10.01.50"')
        data = s.encode()
    elif n == "Metadata/project_settings.config":
        s = data.decode()
        s = re.sub(r'"printer_model_id":\s*"[^"]*"', '"printer_model_id": "BL-P001"', s)
        data = s.encode()
    zout.writestr(n, data)
for n, p in (("Metadata/plate_1.png", png512), ("Metadata/plate_1_small.png", png128),
             ("Metadata/top_1.png", pngtop), ("Metadata/pick_1.png", pngtop), ("Metadata/plate_no_light_1.png", png512)):
    if n not in names:
        zout.write(p, n)
zout.close()
z = zipfile.ZipFile(out); print(out, "->", len(z.namelist()), "entries;", z.testzip() or "zip ok")
