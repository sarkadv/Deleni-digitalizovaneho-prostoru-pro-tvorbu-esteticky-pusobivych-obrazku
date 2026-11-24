"""
Creates the small input images in tests/data/. Run once; the resulting files are committed
and are the fixed inputs of the test suite (re-running is only needed to change them).

    python tests/tools/make_test_images.py
"""

import os
import random

from PIL import Image, ImageDraw

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
DATA = os.path.join(TESTS_DIR, "data")


def blocks():
    """64x48: four solid quadrants and a dark disc - few distinct colours, sharp edges."""
    img = Image.new("RGB", (64, 48))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 23], fill=(200, 30, 30))
    d.rectangle([32, 0, 63, 23], fill=(30, 160, 60))
    d.rectangle([0, 24, 31, 47], fill=(40, 60, 190))
    d.rectangle([32, 24, 63, 47], fill=(245, 245, 235))
    d.ellipse([20, 14, 43, 33], fill=(20, 20, 20))
    img.save(os.path.join(DATA, "blocks.png"))


def blocks_large():
    """512x384: the blocks picture at 8x size - wide enough for visible grid borders (width / 500)."""
    img = Image.new("RGB", (512, 384))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 255, 191], fill=(200, 30, 30))
    d.rectangle([256, 0, 511, 191], fill=(30, 160, 60))
    d.rectangle([0, 192, 255, 383], fill=(40, 60, 190))
    d.rectangle([256, 192, 511, 383], fill=(245, 245, 235))
    d.ellipse([160, 112, 351, 271], fill=(20, 20, 20))
    img.save(os.path.join(DATA, "blocks_large.png"))


def halves():
    """96x64: left half one flat colour, right half random noise."""
    rnd = random.Random(12345)
    img = Image.new("RGB", (96, 64), (120, 140, 160))
    px = img.load()
    for y in range(64):
        for x in range(48, 96):
            px[x, y] = (rnd.randrange(256), rnd.randrange(256), rnd.randrange(256))
    img.save(os.path.join(DATA, "halves.png"))


def photo():
    """120x83 downscaled sample photograph (lossless PNG) + the same picture as JPEG for GUI tests."""
    src = Image.open(os.path.join(PROJECT_ROOT, "img_input", "cat.jpg")).convert("RGB")
    img = src.resize((120, 83), Image.LANCZOS)
    img.save(os.path.join(DATA, "photo.png"))
    img.save(os.path.join(DATA, "photo.jpg"), "JPEG", quality=92)


def gradient():
    """40x30 smooth gradient: many distinct colours, no two neighbours equal."""
    img = Image.new("RGB", (40, 30))
    px = img.load()
    for y in range(30):
        for x in range(40):
            px[x, y] = (x * 6, y * 8, 255 - x * 3 - y * 2)
    img.save(os.path.join(DATA, "gradient.png"))


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    blocks()
    blocks_large()
    halves()
    photo()
    gradient()
    print("written to", DATA)
