# How the tests work

## The idea

There are two programs that should behave the same: the original **Python** program and its **C**
rewrite. Instead of writing the tests twice, there is **one set of tests** that can test either program.

The tests themselves are always written in Python and run with pytest. They never call the program
directly. They call a **backend**: a small translator that passes each call on to the program being tested.

```
                       ┌─ python_backend.py ──►  Python program (util/, geometry/, …)
test_*.py ──► backend ─┤
                       └─ c_backend.py ───────►  C program, compiled into libstylize.dylib
```

You choose the program when you start the tests:

```
pytest                                                       # tests the Python program
pytest --backend=c --c-lib=build/libstylize.dylib --c-app=build/stylize   # tests the C program
```

## Why a translator is needed

Each program uses its own data types. The Python program works with `Point2D` objects and Pillow images;
the C program has its own C structures. The tests use only **plain data** that both sides understand:

| In the tests | Python program | C program |
|---|---|---|
| point `(3, 4)` | `Point2D(3, 4)` | two `int`s |
| colour `(1.0, 0.5, 0.0)` | tuple of floats | three `double`s |
| `RGBImage` (width, height, raw RGB bytes) | Pillow `Image` | byte array |
| `Region` (kind, corners, colour) | `VoronoiRegion` / `DelaunayRegion` / `QuadtreeRegion` | arrays of numbers |

A backend converts plain data into the program's types, calls the program, and converts the answer back.
It contains no checks — all checking happens in the test files, so a backend cannot hide a bug.

## One test, step by step

```python
def test_centroid(backend):
    assert backend.find_polygon_centroid([(0, 0), (3, 0), (0, 3)]) == (1, 1)
```

1. pytest sees the parameter `backend` and asks `conftest.py` for it. `conftest.py` creates the Python
   or the C backend, depending on `--backend`.
2. The test calls `backend.find_polygon_centroid(...)` with plain tuples.
3. The backend converts the tuples (Python: into `Point2D` objects; C: into an `int` array) and calls the
   program's centroid function.
4. The program returns its answer (Python: `Point2D(1, 1)`; C: two `int`s).
5. The backend converts it back to the tuple `(1, 1)`.
6. The test compares it with the expected value.

Steps 1, 2 and 6 are the same for both programs; only steps 3–5 differ.

## Where the expected results come from

* **Written in the test** — for small cases that can be worked out by hand, e.g. the centroid above.
* **`tests/golden/`** — saved results of the Python program for bigger cases: all quadtree regions of an image,
  rendered effect images, decoded JPEG pixels. They were made by `tests/tools/make_golden.py`. The C program
  must produce the same results.
* **Properties** — many parts of the program are random (where points are placed, the paper texture,
  …). The two languages cannot produce the same random numbers, so these tests check what every correct
  result must satisfy: the number of points, that they are inside the image, that they are not too close
  to each other, that the output picture resembles the input, and that the same seed gives the same result.

The input pictures for the tests are in `tests/data/` (made once by `tests/tools/make_test_images.py`).

The full list of what is tested is in [TEST_SCENARIOS.md](TEST_SCENARIOS.md).

## The files

Paths are relative to the `tests/` folder.

| File | Purpose |
|---|---|
| `backends/base.py` | the plain data types and the list of methods every backend must provide |
| `backends/python_backend.py` | backend for the Python program |
| `backends/c_backend.py` | backend for the C program (calls the compiled C library through Python's `ctypes`) |
| `backends/__init__.py` | `load_backend()`: creates the backend chosen by `--backend` |
| `conftest.py` | read by pytest automatically: the command-line options and the shared ready-made values (`backend`, `data_image`, `golden`, `golden_png`, `ui`) |
| `helpers.py` | the tests' own tools (loading images, polygon area, distances, …); never call the program |
| `test_*.py` | the tests |
| `data/`, `golden/` | input pictures and saved reference results |
| `tools/` | scripts that created `data/` and `golden/` |
| `docs/` | this explanation, the list of test scenarios and the README |
| `ui/driver.tcl`, `ui/drivers.py` | tools for the GUI tests (see below) |
| `pytest.ini` (in the project root, one level above `tests/`) | pytest settings (where the tests are, extra output) |

## GUI tests

The GUI tests (`test_ui.py`) do not use a backend. They open the **real program window** and use it like a
person would: they click buttons, choose menu items and read the texts. Three files make this possible.

**`conftest.py` – a clean start for every test.** Before each GUI test, the fixture `ui`:

1. creates an empty temporary folder with what the program needs there: `logo.png`, `img_input/`,
   `img_output/` and `points_output/`;
2. starts the program in that folder (the Python one, or the C one with `--backend=c`);
3. closes the program when the test ends.

So every test starts fresh, and points files and saved pictures never end up in the project.

**`ui/driver.tcl` – the "hands and eyes" inside the program.** Both programs draw their window with Tk
(Python through tkinter, C directly), and this file is loaded into the running program. It can:

* **see** which buttons, labels and menus are visible and what text they show;
* **click** a button or choose a menu item by its text, e.g. `click "Vybrat obrázek"`;
* **replace the dialogs with test versions.** A real file dialog or message box would wait for a person.
  The test version answers at once with what the test asked for, and writes down every message instead
  of showing it.

It only does what a user could do: it does not click hidden widgets, or the main window while the result
window is open. The program's own code is not changed.

**`ui/drivers.py` – the connection between a test and the program.** A test says simple things like
`ui.click("Vybrat obrázek")` or `ui.messages()`; this file turns them into commands for `driver.tcl` and
brings the answers back. There are two versions:

* **Python program** – runs it inside the test itself. If the program crashes, the test fails instead of
  passing silently.
* **C program** – starts it as a separate program and exchanges messages with it (`--test-driver`).

This is why the GUI tests are written only once and work for both programs.

**One test, step by step** – choosing a file that is not a picture:

```python
ui.answer_open_file("/tmp/bad.jpg")     # the next file dialog returns this path
ui.click("Vybrat obrázek")              # press the button; the program tries to open the file
assert ui.messages()[0]["-message"] == "Soubor /tmp/bad.jpg není validní obrázek."
```

The GUI tests open windows on the screen for a moment. `pytest -m ui` runs only them.
