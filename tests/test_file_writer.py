"""Writing the generated points to a text file (util/file_writer.py)."""

import datetime
import os
import re


# FW-01
def test_points_file_format(backend, tmp_path):
    (tmp_path / "points_output").mkdir()
    before = datetime.datetime.now().replace(microsecond=0)
    path = backend.write_points_to_file([(1, 2), (30, 4), (0, 0)], str(tmp_path))
    after = datetime.datetime.now()

    m = re.fullmatch(r"points_output/(\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2})\.txt", path)
    assert m, path
    stamp = datetime.datetime.strptime(m.group(1), "%d-%m-%Y_%H-%M-%S")
    assert before <= stamp <= after

    with open(tmp_path / path, "rb") as f:
        content = f.read().decode("utf-8")
    assert content == ("# počet bodů\n"
                       "3\n"
                       "# souřadnice x;souřadnice y\n"
                       "1;2\n"
                       "30;4\n"
                       "0;0\n")


# FW-02
def test_points_file_empty(backend, tmp_path):
    (tmp_path / "points_output").mkdir()
    path = backend.write_points_to_file([], str(tmp_path))
    with open(os.path.join(tmp_path, path), "rb") as f:
        assert f.read().decode("utf-8") == "# počet bodů\n0\n# souřadnice x;souřadnice y\n"
