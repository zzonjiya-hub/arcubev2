"""v2 markers 생성 (cube 기준, 중앙 80%) + 검증."""
import os
import numpy as np
from PIL import Image

D = r'C:\Users\Kiseok\Desktop\[오픈코드]\KSMS AR큐브 v2'
FIX = os.path.join(D, 'cube')
MD = os.path.join(D, 'markers')
os.makedirs(MD, exist_ok=True)
FACES = ['k', 'c', 'h', 'j', 's', 'm']

def center_crop(img, ratio=0.8):
    w, h = img.size
    cw, ch = int(w * ratio), int(h * ratio)
    return img.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2))

def encode_image(image):
    c16 = center_crop(image.convert('L')).resize((16, 16), Image.LANCZOS)
    blocks = []
    for angle in [0, 90, 180, 270]:
        a = np.asarray(c16.rotate(angle, expand=False, resample=Image.BILINEAR))
        lines = []
        for _ in range(3):
            for y in range(16):
                lines.append(' '.join(f'{v:03d}' for v in a[y]))
        blocks.append('\n'.join(lines))
    return '\n'.join(blocks) + '\n'

for f in FACES:
    img = Image.open(os.path.join(FIX, f'{f}0.jpg'))
    open(os.path.join(MD, f'{f}.patt'), 'w', encoding='utf-8', newline='').write(encode_image(img))
print('markers saved')

def patt16(label):
    lines = open(os.path.join(MD, f'{label}.patt'), encoding='utf-8').read().splitlines()
    ch = []
    for c in range(3):
        ch.append(np.array([[int(v) for v in lines[c * 16 + y].split()] for y in range(16)], float))
    return np.stack(ch).ravel()

def face16(label, angle=0):
    img = Image.open(os.path.join(FIX, f'{label}.jpg' if False else f'{label}0.jpg')).convert('L')
    a = np.asarray(center_crop(img).resize((16, 16), Image.LANCZOS).rotate(
        angle, expand=False, resample=Image.BILINEAR), float)
    return np.stack([a, a, a]).ravel()

pm = {f: patt16(f) for f in FACES}
print('== patt vs face ==')
print('       ' + ' '.join(f'{f:>7s}' for f in FACES))
for a in FACES:
    print(f'patt {a}: ' + ' '.join(f'{np.corrcoef(pm[a], face16(b))[0, 1]:7.3f}' for b in FACES))

print('== rotation robustness ==')
worst = 99
for f in FACES:
    scored = []
    for g in FACES:
        for ang in [0, 90, 180, 270]:
            scored.append((np.corrcoef(pm[f], face16(g, ang))[0, 1], g, ang))
    scored.sort(reverse=True)
    best, runner = scored[0], scored[1]
    margin = best[0] - runner[0]
    worst = min(worst, margin)
    ok = 'PASS' if (best[1] == f and best[2] == 0) else 'FAIL'
    print(f'{f}: best={best[1]}@{best[2]} ({best[0]:.3f}) runner={runner[1]}@{runner[2]} ({runner[0]:.3f}) margin={margin:.3f} {ok}')
print('worst margin:', round(worst, 3))
