"""v2 면 v3: 직각 링 + 고유 이진 스트립(하단) + 원본 글자(상단, 필요시 축소).
검증 포함."""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw

D = r'C:\Users\Kiseok\Desktop\[오픈코드]\KSMS AR큐브 v2'
SRC = os.path.join(D, 'cube')
FIX = os.path.join(D, 'cube')
os.makedirs(FIX, exist_ok=True)
FACES = ['k', 'c', 'h', 'j', 's', 'm']
CODES = {'k': '11011100', 'c': '01000100', 'h': '01101000',
         'j': '11110011', 's': '10110000', 'm': '10010111'}
LETTER_H = {'k': 0.66, 'c': 0.62, 'h': 0.50, 'j': 0.64, 's': 0.68, 'm': 0.76}
MARGIN, THICK = 0.045, 0.07
STRIP_Y0, STRIP_Y1 = 0.80, 0.92
STRIP_X0, STRIP_X1, NCELL = 0.15, 0.85, 8
LETTER_CY, LETTER_MAXB = 0.40, 0.76

def load_gray(path):
    return np.asarray(Image.open(path).convert('L'))

for f in FACES:
    g = load_gray(os.path.join(SRC, f'{f}0.jpg'))
    H, W = g.shape
    dark = (g < 128).astype(np.uint8)
    n, lab, areas, _ = cv2.connectedComponentsWithStats(dark, 8)[:4]
    h, w = lab.shape
    border_ids = set(np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]]))) - {0}
    if border_ids:
        ring_id = max(border_ids, key=lambda i: areas[i, cv2.CC_STAT_AREA])
    else:
        ring_id = int(np.argmax(areas[1:, cv2.CC_STAT_AREA]) + 1)
    letter = np.zeros_like(dark)
    for i in range(1, n):
        if i != ring_id and areas[i, cv2.CC_STAT_AREA] > W * H * 0.0005:
            letter[lab == i] = 1
    # 글자 bbox -> 상단 배치, 하단 0.76 이하로 축소
    ys, xs = np.where(letter)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = letter[y0:y1, x0:x1]
    ch, cw = crop.shape
    max_h = int(H * (LETTER_MAXB - 0.04)) - int(H * 0.04)
    sc = min(1.0, (H * LETTER_H[f]) / ch, (W * 0.72) / cw)
    nw, nh = max(1, int(cw * sc)), max(1, int(ch * sc))
    small = np.asarray(Image.fromarray((crop * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) > 100
    out = np.full((H, W), 255, np.uint8)
    M, T = int(round(W * MARGIN)), int(round(W * THICK))
    out[M:M + T, M:W - M] = 0
    out[H - M - T:H - M, M:W - M] = 0
    out[M:H - M, M:M + T] = 0
    out[M:H - M, W - M - T:W - M] = 0
    oy = int(H * LETTER_CY - nh / 2)
    ox = int(W * 0.5 - nw / 2)
    out[oy:oy + nh, ox:ox + nw][small] = 0
    dr = Image.fromarray(out)
    d2 = ImageDraw.Draw(dr)
    cw_cell = (STRIP_X1 - STRIP_X0) * W / NCELL
    for i, b in enumerate(CODES[f]):
        if b == '1':
            x0c = STRIP_X0 * W + i * cw_cell + 1
            d2.rectangle([x0c, STRIP_Y0 * H, x0c + cw_cell - 2, STRIP_Y1 * H], fill=0)
    out = np.asarray(dr)
    # 글자-테두리/스트립 접촉 검사
    n2, lab2 = cv2.connectedComponents((out < 128).astype(np.uint8), 8)[:2]
    Image.fromarray(out).save(os.path.join(FIX, f'{f}0.jpg'))
    print(f, 'components:', n2 - 1, 'letter_bottom:', round(oy + nh) / H)

# 고정 전개도
FS = 800
GAP = int(FS * 0.13)
Wn, Hn = 4 * FS + 5 * GAP, 3 * FS + 4 * GAP
net = Image.new('RGB', (Wn, Hn), (255, 255, 255))
pos = {'k': (1, 0), 'j': (0, 1), 's': (1, 1), 'c': (2, 1), 'h': (3, 1), 'm': (1, 2)}
for f, (fx, fy) in pos.items():
    img = Image.open(os.path.join(FIX, f'{f}0.jpg')).convert('RGB').resize((FS, FS), Image.LANCZOS)
    net.paste(img, (GAP + fx * (FS + GAP), GAP + fy * (FS + GAP)))
net.save(os.path.join(FIX, '전개도_인쇄용.jpg'), quality=95)
print('net saved', net.size)
