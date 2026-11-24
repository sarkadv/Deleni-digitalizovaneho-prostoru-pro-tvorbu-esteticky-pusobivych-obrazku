"""GUI: the real application window operated like a user does (tests/ui/). File dialogs and message boxes
are replaced by test versions; see tests/docs/HOW_TESTS_WORK.md."""

import os
import re
import shutil

import pytest
from PIL import Image

from ui.drivers import AppError

pytestmark = pytest.mark.ui

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PHOTO_JPG = os.path.join(DATA_DIR, "photo.jpg")     # 120x83

MAIN = ""                                   # title of the main window
RESULT = "Vygenerovaný obrázek"             # title of the result window

PICK_IMAGE = "Vybrat obrázek"
NO_IMAGE_LABEL = "Vybraný obrázek: X"
POINTS_CHECK = "Zapsat vygenerované body do souboru"
PICK_TESSELLATION = "Vybrat teselaci"
PICK_DISTRIBUTION = "Vybrat rozdělení bodů"
PICK_EFFECT = "Vybrat efekt"
GENERATE = "> Generovat"
SHOW = "> Zobrazit"
SAVE = "Uložit obrázek"
BACK = "< Zpět"

VORONOI = "Voroného diagram"
DELAUNAY_FAST = "Delaunayho triangulace - Rychlejší"
DELAUNAY_BETTER = "Delaunayho triangulace - Lepší barvy"
QUADTREE = "Kvadrantový strom"
TESSELLATIONS = [VORONOI, DELAUNAY_FAST, DELAUNAY_BETTER, QUADTREE]

UNIFORM = "Rovnoměrné rozdělení"
NORMAL = "Normální rozdělení - Pravidlo třetin"
ERROR = "Dělení oblastí podle chyby"
MITCHELL = "Mitchellův algoritmus"
LAPLACE_AREA = "Laplaceův operátor - Obsah trojúhelníku"
LAPLACE_LENGTH = "Laplaceův operátor - Délka strany"
LAPLACE_GRADIENT = "Laplaceův operátor - Rozdíl barev vrcholů"

BASIC = "Žádný"
GRID_ONE = "Mřížka - Jednobarevná"
GRID_COLORFUL = "Mřížka - Vícebarevná"
GRADIENTS = "Gradienty"
PAPER = "Papír"
SHAPES = "Různé tvary oblastí"
RECT_OVAL = "Obdélníkové oblasti s ovály"

# what the distribution and effect menus offer after choosing a tessellation (None = no menu)
MENUS = {
    VORONOI: ([UNIFORM, NORMAL, ERROR, MITCHELL], [BASIC, GRID_ONE, GRID_COLORFUL, GRADIENTS, PAPER]),
    DELAUNAY_FAST: ([UNIFORM, NORMAL, LAPLACE_AREA, LAPLACE_LENGTH, LAPLACE_GRADIENT, MITCHELL],
                    [BASIC, GRID_ONE, GRID_COLORFUL, GRADIENTS, PAPER]),
    DELAUNAY_BETTER: ([UNIFORM, NORMAL, LAPLACE_AREA, LAPLACE_LENGTH, LAPLACE_GRADIENT, MITCHELL],
                      [BASIC, GRID_ONE, GRID_COLORFUL, GRADIENTS, PAPER]),
    QUADTREE: (None, [BASIC, GRID_ONE, GRID_COLORFUL, GRADIENTS, SHAPES, RECT_OVAL]),
}

CANVAS = 650        # size of the result window's canvas
FIT = CANVAS - 20   # largest image shown without scaling


# ---- helpers ------------------------------------------------------------------------------------

def controls(ui, window=MAIN):
    """(class, text) of the shown controls a user can read or operate, top to bottom."""
    return [(w.cls, w.text) for w in ui.widgets(window)
            if w.cls in ("Button", "Label", "Checkbutton", "Menubutton") and w.text != ""]


def texts(ui, window=MAIN):
    return [text for _, text in controls(ui, window)]


def check_initial_window(ui):
    assert ui.window_titles() == [MAIN]
    assert controls(ui) == [("Button", PICK_IMAGE), ("Label", NO_IMAGE_LABEL),
                            ("Checkbutton", POINTS_CHECK), ("Menubutton", PICK_TESSELLATION)]
    assert [w.value for w in ui.widgets() if w.cls == "Checkbutton"] == ["0"]
    # the logo: a label with an image above the controls
    logo = [w for w in ui.widgets() if w.cls == "Label" and w.text == ""]
    assert len(logo) == 1 and logo[0].y < ui.widgets()[-1].y


def pick_image(ui, path):
    ui.answer_open_file(path)
    ui.click(PICK_IMAGE)


def choose_all(ui, tessellation, distribution, effect):
    ui.choose(PICK_TESSELLATION, tessellation)
    if distribution is not None:
        ui.choose(PICK_DISTRIBUTION, distribution)
    ui.choose(PICK_EFFECT, effect)


def generate(ui, path=PHOTO_JPG, tessellation=QUADTREE, distribution=None, effect=BASIC):
    """Picks the image and options and clicks Generovat; no message may appear."""
    pick_image(ui, path)
    choose_all(ui, tessellation, distribution, effect)
    ui.clear_log()
    ui.click(GENERATE)
    assert messages(ui) == []


def show_result(ui, **options):
    generate(ui, **options)
    ui.click(SHOW)
    assert RESULT in ui.window_titles()


def two_tone_jpeg(directory, width, height):
    """A JPEG with a left and a right half of two flat colours (fast to stylise at any size)."""
    image = Image.new("RGB", (width, height), (200, 60, 40))
    image.paste((40, 90, 200), (width // 2, 0, width, height))
    path = os.path.join(directory, f"two_tone_{width}x{height}.jpg")
    image.save(path, quality=95)
    return path


def messages(ui):
    """Message boxes shown since clear_log() as (icon, title, text). Only these are compared, so that the
    same message box made with other default options (e.g. -parent) also passes; it must be an OK box."""
    result = []
    for m in ui.messages():
        assert m.get("-type", "ok") == "ok"
        result.append((m.get("-icon", "info"), m["-title"], m["-message"]))
    return result


def same_dir(path, expected):
    """path names the folder expected (relative to the working directory), with or without a final /."""
    return os.path.normpath(path) == expected


def points_files(ui):
    return sorted(os.listdir(os.path.join(ui.workdir, "points_output")))


# ---- main window --------------------------------------------------------------------------------

# UI-01
def test_initial_window(ui):
    check_initial_window(ui)
    main = ui.windows()[0]
    assert (main["width"], main["height"]) == (350, 550)


# UI-02
def test_tessellation_menu_items(ui):
    assert ui.menu_items(PICK_TESSELLATION) == TESSELLATIONS


# UI-03
@pytest.mark.parametrize("tessellation", TESSELLATIONS)
def test_menus_offered_for_tessellation(ui, tessellation):
    distributions, effects = MENUS[tessellation]
    ui.choose(PICK_TESSELLATION, tessellation)

    expected = [("Button", PICK_IMAGE), ("Label", NO_IMAGE_LABEL), ("Checkbutton", POINTS_CHECK),
                ("Menubutton", tessellation)]
    if distributions is not None:
        expected.append(("Menubutton", PICK_DISTRIBUTION))
    expected += [("Menubutton", PICK_EFFECT), ("Button", GENERATE)]
    assert controls(ui) == expected

    if distributions is not None:
        assert ui.menu_items(PICK_DISTRIBUTION) == distributions
    assert ui.menu_items(PICK_EFFECT) == effects
    assert ui.menu_items(tessellation) == TESSELLATIONS


# UI-04
def test_changing_tessellation_replaces_menus(ui):
    ui.choose(PICK_TESSELLATION, VORONOI)
    ui.choose(PICK_DISTRIBUTION, ERROR)
    ui.choose(PICK_EFFECT, PAPER)

    ui.choose(VORONOI, QUADTREE)
    assert controls(ui)[3:] == [("Menubutton", QUADTREE), ("Menubutton", PICK_EFFECT), ("Button", GENERATE)]
    assert ui.menu_items(PICK_EFFECT) == MENUS[QUADTREE][1]

    ui.choose(QUADTREE, DELAUNAY_FAST)
    assert controls(ui)[3:] == [("Menubutton", DELAUNAY_FAST), ("Menubutton", PICK_DISTRIBUTION),
                                ("Menubutton", PICK_EFFECT), ("Button", GENERATE)]
    assert ui.menu_items(PICK_DISTRIBUTION) == MENUS[DELAUNAY_FAST][0]
    assert ui.menu_items(PICK_EFFECT) == MENUS[DELAUNAY_FAST][1]


# UI-05
def test_chosen_items_are_shown(ui):
    choose_all(ui, DELAUNAY_BETTER, LAPLACE_LENGTH, GRADIENTS)
    assert [t for c, t in controls(ui) if c == "Menubutton"] == [DELAUNAY_BETTER, LAPLACE_LENGTH, GRADIENTS]
    ui.choose(LAPLACE_LENGTH, MITCHELL)
    ui.choose(GRADIENTS, GRID_ONE)
    assert [t for c, t in controls(ui) if c == "Menubutton"] == [DELAUNAY_BETTER, MITCHELL, GRID_ONE]


# UI-06
def test_points_checkbox_toggles(ui):
    ui.click(POINTS_CHECK)
    assert [w.value for w in ui.widgets() if w.cls == "Checkbutton"] == ["1"]
    ui.click(POINTS_CHECK)
    assert [w.value for w in ui.widgets() if w.cls == "Checkbutton"] == ["0"]


# ---- choosing the image -------------------------------------------------------------------------

# UI-07
def test_pick_image(ui):
    pick_image(ui, PHOTO_JPG)
    calls = ui.dialogs()
    assert len(calls) == 1
    kind, options = calls[0]
    assert kind == "open"
    assert options["-title"] == "Vybrat obrázek"
    assert same_dir(options["-initialdir"], "img_input")
    assert re.findall(r"\*\.\w+", options["-filetypes"]) == ["*.jpg", "*.jpeg"]
    assert "Vybraný obrázek: photo.jpg" in texts(ui)
    assert NO_IMAGE_LABEL not in texts(ui)


# UI-08
def test_long_file_name_is_shortened(ui, tmp_path):
    path = tmp_path / "a_very_long_name_of_the_photo.jpg"
    shutil.copy(PHOTO_JPG, path)
    pick_image(ui, str(path))
    assert "Vybraný obrázek: a_very_long_name_of_..." in texts(ui)


# UI-09
def test_cancel_keeps_previous_image(ui):
    pick_image(ui, PHOTO_JPG)
    pick_image(ui, "")      # Cancel in the dialog
    assert "Vybraný obrázek: photo.jpg" in texts(ui)
    assert messages(ui) == []

    # the program still has the picture, not only the label: generating works
    choose_all(ui, QUADTREE, None, BASIC)
    ui.click(GENERATE)
    assert messages(ui) == []
    assert SHOW in texts(ui)


# UI-10
@pytest.mark.parametrize("content", [b"", b"this is not a picture", None], ids=["empty", "text", "missing"])
def test_invalid_image_file(ui, tmp_path, content):
    pick_image(ui, PHOTO_JPG)
    path = tmp_path / "bad.jpg"
    if content is not None:
        path.write_bytes(content)
    ui.clear_log()
    pick_image(ui, str(path))
    assert messages(ui) == [("error", "Chyba", "Soubor " + str(path) + " není validní obrázek.")]
    assert NO_IMAGE_LABEL in texts(ui)

    # the previously chosen picture is forgotten
    ui.choose(PICK_TESSELLATION, QUADTREE)
    ui.choose(PICK_EFFECT, BASIC)
    ui.clear_log()
    ui.click(GENERATE)
    assert [text for _, _, text in messages(ui)] == ["Nebyl vybrán obrázek."]


# ---- missing choices ----------------------------------------------------------------------------

def error_after_generate(ui):
    ui.clear_log()
    ui.click(GENERATE)
    shown = messages(ui)
    assert [(icon, title) for icon, title, _ in shown] == [("error", "Chyba")]
    assert controls(ui)[0] == ("Button", PICK_IMAGE)     # still in the options window
    return shown[0][2]


# UI-11
def test_missing_image(ui):
    choose_all(ui, VORONOI, UNIFORM, BASIC)
    assert error_after_generate(ui) == "Nebyl vybrán obrázek."


# UI-12
def test_missing_tessellation(ui):
    # Generovat is offered only once a tessellation is chosen
    pick_image(ui, PHOTO_JPG)
    assert GENERATE not in texts(ui)
    with pytest.raises(AppError):
        ui.click(GENERATE)


# UI-13
@pytest.mark.parametrize("tessellation", [VORONOI, DELAUNAY_FAST, DELAUNAY_BETTER])
def test_missing_distribution(ui, tessellation):
    pick_image(ui, PHOTO_JPG)
    ui.choose(PICK_TESSELLATION, tessellation)
    ui.choose(PICK_EFFECT, BASIC)
    assert error_after_generate(ui) == "Nebylo vybráno rozdělení bodů."


# UI-14
@pytest.mark.parametrize("tessellation, distribution", [(VORONOI, UNIFORM), (QUADTREE, None)])
def test_missing_effect(ui, tessellation, distribution):
    pick_image(ui, PHOTO_JPG)
    ui.choose(PICK_TESSELLATION, tessellation)
    if distribution is not None:
        ui.choose(PICK_DISTRIBUTION, distribution)
    assert error_after_generate(ui) == "Nebyl vybrán efekt."


# UI-24
@pytest.mark.parametrize("first, second, missing", [
    ((QUADTREE, None, BASIC), VORONOI, "Nebylo vybráno rozdělení bodů."),
    ((VORONOI, ERROR, PAPER), DELAUNAY_FAST, "Nebylo vybráno rozdělení bodů."),
    ((VORONOI, UNIFORM, PAPER), QUADTREE, "Nebyl vybrán efekt."),
], ids=["quadtree-voronoi", "voronoi-delaunay", "voronoi-quadtree"])
def test_changing_tessellation_forgets_choices(ui, first, second, missing):
    # the menus show their prompts again, so the earlier choices must not be used
    pick_image(ui, PHOTO_JPG)
    choose_all(ui, *first)
    ui.choose(first[0], second)
    assert error_after_generate(ui) == missing


# ---- generating ---------------------------------------------------------------------------------

# UI-15
@pytest.mark.parametrize("tessellation, distribution, effect",
                         [(VORONOI, UNIFORM, BASIC), (DELAUNAY_FAST, NORMAL, GRID_ONE), (QUADTREE, None, SHAPES)])
def test_generate_without_points_file(ui, tessellation, distribution, effect):
    generate(ui, tessellation=tessellation, distribution=distribution, effect=effect)
    assert controls(ui) == [("Label", "Generování obrázku..."), ("Label", "Body byly vygenerovány."),
                            ("Label", "Obrázek byl vygenerován!"), ("Button", SHOW)]
    assert points_files(ui) == []


# UI-16
def test_generate_with_points_file(ui):
    ui.click(POINTS_CHECK)
    generate(ui, tessellation=VORONOI, distribution=UNIFORM, effect=BASIC)

    files = points_files(ui)
    assert len(files) == 1 and re.fullmatch(r"\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}\.txt", files[0])
    assert controls(ui) == [("Label", "Generování obrázku..."),
                            ("Label", "Vygenerované body uloženy do souboru:\npoints_output/" + files[0]),
                            ("Label", "Obrázek byl vygenerován!"), ("Button", SHOW)]

    with open(os.path.join(ui.workdir, "points_output", files[0]), encoding="utf-8") as f:
        lines = f.read().splitlines()
    assert lines[0] == "# počet bodů"
    assert lines[2] == "# souřadnice x;souřadnice y"
    count = int(lines[1])
    assert count > 0 and len(lines) == 3 + count
    for line in lines[3:]:
        x, y = map(int, line.split(";"))
        assert 1 <= x < 120 and 1 <= y < 83


# ---- result window ------------------------------------------------------------------------------

# UI-17
def test_result_window(ui):
    show_result(ui, tessellation=VORONOI, distribution=UNIFORM, effect=BASIC)
    result = [w for w in ui.windows() if w["title"] == RESULT]
    assert len(result) == 1 and (result[0]["width"], result[0]["height"]) == (725, 725)
    assert controls(ui, RESULT) == [("Button", SAVE), ("Button", BACK)]

    canvases = [w for w in ui.widgets(RESULT) if w.cls == "Canvas"]
    assert len(canvases) == 1
    # the picture is small enough, so it is shown unscaled in the middle of the canvas
    assert ui.canvas_images(RESULT) == [{"image": ui.canvas_images(RESULT)[0]["image"], "anchor": "nw",
                                         "x": (CANVAS - 120) // 2, "y": (CANVAS - 83) // 2,
                                         "width": 120, "height": 83}]

    # the result window is modal: the main window cannot be used while it is open
    with pytest.raises(AppError, match="grab"):
        ui.click(SHOW)


# UI-18
@pytest.mark.parametrize("size, shown", [
    ((FIT, 400), (FIT, 400)),                               # exactly as wide as the limit: not scaled
    ((400, FIT), (400, FIT)),
    ((FIT + 1, 400), (FIT, int(FIT * 400 / (FIT + 1)))),    # one pixel too wide: scaled down
    ((400, FIT + 1), (int(FIT * 400 / (FIT + 1)), FIT)),
    ((1024, 768), (FIT, int(FIT * 768 / 1024))),
    ((768, 1024), (int(FIT * 768 / 1024), FIT)),
    ((1000, 649), (FIT, int(FIT * 649 / 1000))),            # 408.87 -> 408: rounded down
    ((649, 1000), (int(FIT * 649 / 1000), FIT)),
    ((700, 700), (FIT, FIT)),
], ids=lambda v: "x".join(map(str, v)))
def test_result_image_scaled_to_fit(ui, tmp_path, size, shown):
    show_result(ui, path=two_tone_jpeg(str(tmp_path), *size))
    images = ui.canvas_images(RESULT)
    assert len(images) == 1
    image = images[0]
    assert (image["width"], image["height"]) == shown
    assert image["anchor"] == "nw"
    assert (image["x"], image["y"]) == ((CANVAS - shown[0]) // 2, (CANVAS - shown[1]) // 2)


# ---- saving -------------------------------------------------------------------------------------

# UI-19
def test_save_png(ui):
    show_result(ui, tessellation=VORONOI, distribution=UNIFORM, effect=BASIC)
    target = os.path.join(ui.workdir, "img_output", "result.png")
    ui.answer_save_file(target)
    ui.clear_log()
    ui.click(SAVE)

    (kind, options), _ = ui.dialogs()
    assert kind == "save"
    assert options["-title"] == "Uložit obrázek"
    assert same_dir(options["-initialdir"], "img_output")
    assert options["-defaultextension"] == ".png"
    assert re.findall(r"\*\.\w+", options["-filetypes"]) == ["*.png"]
    assert messages(ui) == [("info", "Success", "Vygenerovaný obrázek uložen do souboru:\n" + target)]

    with open(target, "rb") as f:
        assert f.read(8) == b"\x89PNG\r\n\x1a\n"
    saved = Image.open(target)
    assert saved.mode == "RGBA" and saved.size == (120, 83)

    # the saved picture is the one shown in the result window (compared where it is fully opaque)
    shown = ui.canvas_images(RESULT)[0]["image"]
    compared = 0
    for y in range(0, 83, 7):
        for x in range(0, 120, 7):
            r, g, b, a = saved.getpixel((x, y))
            if a == 255:
                assert ui.image_pixel(shown, x, y) == (r, g, b)
                compared += 1
    assert compared > 50

    # the picture still resembles the input
    photo = Image.open(PHOTO_JPG).convert("RGB")
    diff = sum(abs(p - q) for x in range(0, 120, 5) for y in range(0, 83, 5)
               for p, q in zip(saved.getpixel((x, y))[:3], photo.getpixel((x, y))))
    assert diff / (24 * 17 * 3) < 40


# UI-20
def test_save_cancelled(ui):
    show_result(ui)
    ui.answer_save_file("")
    ui.clear_log()
    ui.click(SAVE)
    assert [kind for kind, _ in ui.dialogs()] == ["save"]
    assert os.listdir(os.path.join(ui.workdir, "img_output")) == []
    assert RESULT in ui.window_titles()


# UI-21
def test_save_fails(ui):
    show_result(ui)
    ui.answer_save_file(os.path.join(ui.workdir, "no_such_folder", "result.png"))
    ui.clear_log()
    ui.click(SAVE)
    assert messages(ui) == [("error", "Error", "Nepodařilo se uložit obrázek.")]
    assert RESULT in ui.window_titles()


# ---- going back ---------------------------------------------------------------------------------

# UI-22
@pytest.mark.parametrize("how", ["back_button", "close_window"])
def test_back_resets_window(ui, how):
    ui.click(POINTS_CHECK)
    show_result(ui, tessellation=VORONOI, distribution=UNIFORM, effect=GRID_COLORFUL)
    if how == "back_button":
        ui.click(BACK)
    else:
        ui.close_window(RESULT)

    check_initial_window(ui)

    # nothing chosen before is remembered
    ui.choose(PICK_TESSELLATION, VORONOI)
    ui.choose(PICK_DISTRIBUTION, UNIFORM)
    ui.choose(PICK_EFFECT, BASIC)
    ui.clear_log()
    ui.click(GENERATE)
    assert [text for _, _, text in messages(ui)] == ["Nebyl vybrán obrázek."]


# UI-23
def test_generate_again_after_back(ui, tmp_path):
    ui.click(POINTS_CHECK)
    show_result(ui, tessellation=QUADTREE, effect=RECT_OVAL)
    for name in points_files(ui):
        os.remove(os.path.join(ui.workdir, "points_output", name))
    ui.click(BACK)

    # a picture of another size, so that the old result cannot pass for the new one
    show_result(ui, path=two_tone_jpeg(str(tmp_path), 200, 150),
                tessellation=DELAUNAY_BETTER, distribution=UNIFORM, effect=BASIC)
    image = ui.canvas_images(RESULT)[0]
    assert (image["width"], image["height"]) == (200, 150)
    # the check box was reset to unchecked, and so was what the program does with it
    assert points_files(ui) == []
