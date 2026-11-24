"""Loading input JPEG images and saving the generated PNG."""

import hashlib
import os

import pytest
from PIL import Image

from backends import RGBAImage
from conftest import PROJECT_ROOT, DATA_DIR

SAMPLES = ["audrey_hepburn.jpg", "cassie_trava.jpeg", "cat.jpg", "galaxie.jpeg", "girl_with_a_pearl_earring.jpg",
           "kvetiny.jpg", "les.jpg", "mesto.jpg", "mickey_mouse.jpg", "mona_lisa.jpg", "pizza.jpeg", "poust.jpeg",
           "textura.jpg", "tulen.jpg"]


# IO-01
@pytest.mark.parametrize("name", SAMPLES)
def test_sample_images_decode_identically(backend, golden, name):
    """Decoded pixels must match the reference decoder exactly (same JPEG decoding, EXIF rotation)."""
    expected = golden("image_decoding")[name]
    img = backend.load_image(os.path.join(PROJECT_ROOT, "img_input", name))
    assert [img.width, img.height] == expected["size"]
    assert hashlib.sha256(img.data).hexdigest() == expected["sha256"]


# IO-02
def test_test_photo_decodes_identically(backend, golden):
    expected = golden("image_decoding")["tests/data/photo.jpg"]
    img = backend.load_image(os.path.join(DATA_DIR, "photo.jpg"))
    assert [img.width, img.height] == expected["size"]
    assert hashlib.sha256(img.data).hexdigest() == expected["sha256"]


# IO-03
def test_exif_orientation_is_applied(backend):
    # cassie_trava.jpeg is stored 4032x3024 with EXIF orientation 6 (rotate 90 degrees)
    img = backend.load_image(os.path.join(PROJECT_ROOT, "img_input", "cassie_trava.jpeg"))
    assert (img.width, img.height) == (3024, 4032)


# IO-04
def test_grayscale_jpeg_becomes_rgb(backend):
    img = backend.load_image(os.path.join(PROJECT_ROOT, "img_input", "audrey_hepburn.jpg"))
    assert len(img.data) == img.width * img.height * 3
    assert all(img.data[i] == img.data[i + 1] == img.data[i + 2] for i in range(0, 3 * 5000, 3))


# IO-05
def test_save_png_roundtrip(backend, tmp_path):
    w, h = 7, 5
    data = b"".join(bytes(t) for t in
                    [(x * 30, y * 40, (x + y) * 10, [255, 128, 0, 77][(x + y) % 4]) for y in range(h) for x in range(w)])
    path = tmp_path / "out.png"
    backend.save_png(RGBAImage(w, h, data), str(path))
    with Image.open(path) as saved:
        assert saved.format == "PNG"
        assert saved.mode == "RGBA"
        assert saved.size == (w, h)
        assert saved.tobytes() == data
