"""Basit z-tamponlu yuzey kaplayici -- parcalarin PNG onizlemesi icin."""
import numpy as np
from PIL import Image

BG = (250, 250, 248)


def _shade(mesh, size, elev, azim, light=(-0.4, -0.6, 0.75), color=(214, 96, 52),
           pad=1.12):
    v = mesh.vertices - mesh.bounds.mean(axis=0)
    ce, se = np.cos(np.radians(elev)), np.sin(np.radians(elev))
    ca, sa = np.cos(np.radians(azim)), np.sin(np.radians(azim))
    Rz = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, ce, -se], [0, se, ce]])
    v = v @ Rz.T @ Rx.T
    # ekran: x saga, z yukari, -y derinlik
    # kamera -Y'de: kucuk y = izleyiciye yakin -> derinlik anahtari -y
    px, py, pz = v[:, 0], v[:, 2], -v[:, 1]
    span = max(px.max() - px.min(), py.max() - py.min()) * pad
    s = size / span
    sx = (px - (px.max() + px.min()) / 2) * s + size / 2
    sy = size / 2 - (py - (py.max() + py.min()) / 2) * s

    f = mesh.faces
    n = mesh.face_normals @ Rz.T @ Rx.T
    L = np.array(light, float)
    L /= np.linalg.norm(L)
    lam = np.clip(n @ L, 0, 1)
    spec = np.clip(-n[:, 1] * 0.6 + n[:, 2] * 0.5, 0, 1) ** 14
    shade = 0.26 + 0.70 * lam
    if color is None:                       # yuz renkleri meshten gelir
        base = np.asarray(mesh.visual.face_colors[:, :3], float)
    else:
        base = np.tile(np.asarray(color, float), (len(mesh.faces), 1))
    col = np.clip(base * shade[:, None] + np.outer(spec, [110, 110, 110]), 0, 255)

    img = np.zeros((size, size, 3), float)
    img[:] = BG
    zbuf = np.full((size, size), -1e18)
    tx, ty, tz = sx[f], sy[f], pz[f]
    # arkadan one sirala (kaba on siralama hizlandirir)
    order = np.argsort(tz.mean(axis=1))[::-1]
    for i in order:
        x0, x1, x2 = tx[i]
        y0, y1, y2 = ty[i]
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if area >= -1e-9:                        # arka yuz
            continue
        xlo = max(int(np.floor(min(x0, x1, x2))), 0)
        xhi = min(int(np.ceil(max(x0, x1, x2))) + 1, size)
        ylo = max(int(np.floor(min(y0, y1, y2))), 0)
        yhi = min(int(np.ceil(max(y0, y1, y2))) + 1, size)
        if xlo >= xhi or ylo >= yhi:
            continue
        X, Y = np.meshgrid(np.arange(xlo, xhi) + 0.5, np.arange(ylo, yhi) + 0.5)
        w0 = ((x1 - x0) * (Y - y0) - (X - x0) * (y1 - y0)) / area
        w1 = ((x2 - x1) * (Y - y1) - (X - x1) * (y2 - y1)) / area
        w2 = 1.0 - w0 - w1
        m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not m.any():
            continue
        z = w1 * tz[i, 0] + w2 * tz[i, 1] + w0 * tz[i, 2]
        sub = zbuf[ylo:yhi, xlo:xhi]
        hit = m & (z > sub)
        if not hit.any():
            continue
        sub[hit] = z[hit]
        img[ylo:yhi, xlo:xhi][hit] = col[i]
    return img


def render(mesh, path, size=760, elev=22, azim=32, color=(214, 96, 52), ss=2):
    img = _shade(mesh, size * ss, elev, azim, color=color)
    im = Image.fromarray(img.astype(np.uint8)).resize((size, size), Image.LANCZOS)
    im.save(path)
    return path


def render_row(meshes, path, size=560, elev=22, azim=32, colors=None, ss=2):
    colors = colors or [(214, 96, 52)] * len(meshes)
    tiles = [Image.fromarray(_shade(m, size * ss, elev, azim, color=c).astype(np.uint8))
             .resize((size, size), Image.LANCZOS) for m, c in zip(meshes, colors)]
    out = Image.new("RGB", (size * len(tiles), size), BG)
    for i, t in enumerate(tiles):
        out.paste(t, (i * size, 0))
    out.save(path)
    return path
