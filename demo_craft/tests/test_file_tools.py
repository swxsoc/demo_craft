import pytest

from demo_craft import _test_files_directory
from demo_craft.io.file_tools import read_file


def test_read_file():
    table = read_file(
        _test_files_directory / "demo_craft_l0_20260101T000000_v0.0.1.csv"
    )
    assert table.colnames == ["time", "counts"]
    assert len(table) == 60
    assert table["time"][0] == "2026-01-01T00:00:00.000"
    assert table["counts"][0] == 1000


def test_read_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_file(tmp_path / "missing.csv")


def test_read_file_wrong_extension(tmp_path):
    with pytest.raises(ValueError):
        read_file(tmp_path / "test_file.cdf")
