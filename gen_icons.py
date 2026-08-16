import zlib, struct, os

# 纯 Python PNG 编码器（零依赖），绘制一枚书签图标。
BG = (43, 125, 233)   # 蓝
FG = (255, 255, 255)  # 白

def in_mark(x, y, S):
    """书签形状：矩形 + 底部 V 形缺口（经典书签尾）。坐标相对中心归一化。"""
    left, right = 0.25 * S, 0.75 * S
    top, bottom = 0.15 * S, 0.85 * S
    if not (left <= x <= right and top <= y <= bottom):
        return False
    # 底部 V 缺口：y 在 [0.60S, 0.85S] 之间，中心处挖掉一个向上的三角形
    if y >= 0.60 * S:
        half = (y - 0.60 * S) / (0.85 * S - 0.60 * S) * (0.125 * S)
        if abs(x - 0.5 * S) < half:
            return False
    return True

def make_icon(size, path):
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # 每行前缀 filter byte = 0 (None)
        for x in range(size):
            c = FG if in_mark(x, y, size) else BG
            raw += bytes(c)
    def chunk(typ, data):
        return (struct.pack('>I', len(data)) + typ + data +
                struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff))
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)  # 8bit, RGB
    idat = zlib.compress(bytes(raw), 9)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
           chunk(b'IDAT', idat) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    print('wrote', path, size, 'px')

out = os.path.join(os.path.dirname(__file__), 'icons')
os.makedirs(out, exist_ok=True)
for s in (16, 48, 128):
    make_icon(s, os.path.join(out, f'icon{s}.png'))
