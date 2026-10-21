"""Clear the haze from auction/yard car photos and deepen black paint, then prepare them for a poster.

Usage:
  python3 templates/midas-motors/tools/enhance_photo.py IN OUT [--plate x0,y0,x1,y1 ...] [--crop x0,y0,x1,y1]
                                                         [--strength 1.0] [--width 1600]

  --plate     blur a number-plate box (source pixels); repeatable
  --crop      keep only this box (source pixels), e.g. to cut a dealer watermark off the bottom
  --strength  0 = untouched, 1 = default, up to ~1.5 for very washed-out photos
  --width     upscale to this width (Lanczos + light sharpening); 0 keeps the size
Needs: pip install opencv-python-headless (brings numpy).
"""
import argparse

import cv2
import numpy as np


def enhance(bgr, strength=1.0):
    img = bgr.astype(np.float32) / 255.0
    # 1. Levels: auction photos have grey "lifted" blacks and dull whites. Stretch on luminance so colours do not shift.
    lum = img @ np.array([0.114, 0.587, 0.299], dtype=np.float32)
    lo, hi = np.percentile(lum, 0.5), np.percentile(lum, 99.7)
    lo *= strength
    hi = 1.0 - (1.0 - hi) * strength
    img = np.clip((img - lo) / max(hi - lo, 1e-3), 0, 1)

    lab = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2LAB)
    L, a, b = cv2.split(lab)
    # 2. Gentle local contrast (CLAHE, half-blended) on lightness only: brings back reflections and panel
    #    lines lost in the haze without turning concrete floors and walls blotchy.
    if strength > 0:
        Lc = cv2.createCLAHE(clipLimit=1.0 + 0.5 * strength, tileGridSize=(4, 4)).apply(L)
        L = cv2.addWeighted(Lc, 0.5, L, 0.5, 0)
    Lf = L.astype(np.float32) / 255.0
    # 3. Tone curve: push the darkest tones down (deep black paint) and leave mid-greys and highlights alone.
    k = 0.6 * strength
    Lf = Lf - k * Lf * (1 - Lf) ** 3 * 2.2
    Lf = np.clip(Lf, 0, 1)
    # 4. Black paint reads purple/blue under garage lights: neutralise colour where it is dark, not in lights or panels.
    w = np.clip((0.42 - Lf) / 0.42, 0, 1) ** 0.7 * min(strength, 1.0)
    a = (a.astype(np.float32) - 128) * (1 - 0.9 * w) + 128
    b = (b.astype(np.float32) - 128) * (1 - 0.9 * w) + 128
    lab = cv2.merge([(Lf * 255).round().astype(np.uint8), a.clip(0, 255).astype(np.uint8), b.clip(0, 255).astype(np.uint8)])
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    # 5. A touch more saturation outside the black areas (lamps, interior trim, sky).
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + 0.12 * strength * (1 - w)), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def blur_plate(bgr, box):
    x0, y0, x1, y1 = box
    roi = bgr[y0:y1, x0:x1]
    k = max(15, (min(x1 - x0, y1 - y0) // 2) | 1)
    bgr[y0:y1, x0:x1] = cv2.GaussianBlur(cv2.GaussianBlur(roi, (k, k), 0), (k, k), 0)
    return bgr


def upscale(bgr, width):
    h, w = bgr.shape[:2]
    if not width or width <= w:
        return bgr
    big = cv2.resize(bgr, (width, round(width * h / w)), interpolation=cv2.INTER_LANCZOS4)
    soft = cv2.GaussianBlur(big, (0, 0), 2.0)
    return cv2.addWeighted(big, 1.6, soft, -0.6, 0)  # unsharp mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--plate', action='append', default=[], help='x0,y0,x1,y1 in source pixels')
    ap.add_argument('--crop', help='x0,y0,x1,y1 in source pixels')
    ap.add_argument('--strength', type=float, default=1.0)
    ap.add_argument('--width', type=int, default=1600)
    args = ap.parse_args()
    bgr = cv2.imread(args.src, cv2.IMREAD_COLOR)
    if bgr is None:
        raise SystemExit('cannot read ' + args.src)
    cx, cy = 0, 0
    if args.crop:  # crop first so the watermark does not skew the levels; plate boxes stay in source pixels
        cx, cy, x1, y1 = [int(v) for v in args.crop.split(',')]
        bgr = bgr[cy:y1, cx:x1].copy()
    if args.strength > 0:  # 0 = leave an already clean photo untouched (plate blur / resize only)
        bgr = enhance(bgr, args.strength)
    for p in args.plate:
        x0, y0, x1, y1 = [int(v) for v in p.split(',')]
        bgr = blur_plate(bgr, [x0 - cx, y0 - cy, x1 - cx, y1 - cy])
    bgr = upscale(bgr, args.width)
    cv2.imwrite(args.dst, bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('✓', args.dst, bgr.shape[1], 'x', bgr.shape[0])


if __name__ == '__main__':
    main()
