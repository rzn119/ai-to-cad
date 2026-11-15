"""Crop the renders to their content (height-joint sections: to the box wall region)."""
import sys
from pathlib import Path
from PIL import Image, ImageChops

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "renders")


def content_box(im):
    bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 18 else 0)
    return diff.getbbox()


def cream_box(im):
    px = im.load()
    xs, ys = [], []
    for y in range(0, im.height, 3):
        for x in range(0, im.width, 3):
            r, g, b = px[x, y][:3]
            if r > 200 and g > 190 and r - b > 18 and r - b < 60:
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


for p in sorted(folder.glob("*.png")):
    im = Image.open(p).convert("RGB")
    box = content_box(im)
    if p.name.startswith("2-") and p.name.endswith("_detail.png"):
        cb = cream_box(im)
        if cb:
            box = (box[0], max(box[1], cb[1] - 160), box[2], min(box[3], cb[3] + 160))
    m = 30
    box = (max(0, box[0] - m), max(0, box[1] - m), min(im.width, box[2] + m), min(im.height, box[3] + m))
    im.crop(box).save(p)
    print(p.name, im.crop(box).size)
