"""
Shared pytest configuration.

Select the implementation under test:
    pytest                                   # Python implementation (default)
    pytest --backend=c --c-lib=<libstylize> --c-app=<stylize executable>
Options can also be given as environment variables STYLIZE_BACKEND, STYLIZE_C_LIB,
STYLIZE_C_APP and STYLIZE_PYTHON_ROOT.
"""

import json
import os

import pytest

from backends import load_backend
from helpers import load_png_rgb

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
DATA_DIR = os.path.join(TESTS_DIR, "data")
GOLDEN_DIR = os.path.join(TESTS_DIR, "golden")


def pytest_addoption(parser):
    parser.addoption("--backend", default=os.environ.get("STYLIZE_BACKEND", "python"),
                     choices=["python", "c"], help="implementation under test")
    parser.addoption("--python-root", default=os.environ.get("STYLIZE_PYTHON_ROOT", PROJECT_ROOT),
                     help="root directory of the Python implementation")
    parser.addoption("--c-lib", default=os.environ.get("STYLIZE_C_LIB"),
                     help="path to the C shared library (libstylize)")
    parser.addoption("--c-app", default=os.environ.get("STYLIZE_C_APP"),
                     help="path to the C GUI executable")


def pytest_report_header(config):
    return "stylize backend: " + config.getoption("--backend")


@pytest.fixture(scope="session")
def backend(pytestconfig):
    return load_backend(pytestconfig.getoption("--backend"),
                        python_root=pytestconfig.getoption("--python-root"),
                        c_lib=pytestconfig.getoption("--c-lib"))


@pytest.fixture(scope="session")
def data_image():
    """data_image("blocks") -> RGBImage of tests/data/blocks.png"""
    cache = {}

    def load(name):
        if name not in cache:
            cache[name] = load_png_rgb(os.path.join(DATA_DIR, name + ".png"))
        return cache[name]
    return load


@pytest.fixture(scope="session")
def golden():
    """golden("quadtree_regions") -> parsed tests/golden/quadtree_regions.json"""
    cache = {}

    def load(name):
        if name not in cache:
            with open(os.path.join(GOLDEN_DIR, name + ".json"), encoding="utf-8") as f:
                cache[name] = json.load(f)
        return cache[name]
    return load


@pytest.fixture(scope="session")
def golden_png():
    """golden_png("render_x") -> RGBAImage of tests/golden/render_x.png"""
    from helpers import load_png_rgba
    return lambda name: load_png_rgba(os.path.join(GOLDEN_DIR, name + ".png"))
