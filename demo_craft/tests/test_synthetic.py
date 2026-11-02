from datetime import UTC, datetime

from demo_craft import _test_files_directory
from demo_craft.util.synthetic import DEFAULT_TIME, l0_rows, write_l0_file

L0_NAME = "demo_craft_l0_20260101T000000_v0.0.1.csv"


def test_bundled_file_is_reproducible(tmp_path):
    regenerated = write_l0_file(tmp_path)
    assert regenerated.name == L0_NAME
    assert regenerated.read_bytes() == (_test_files_directory / L0_NAME).read_bytes()


def test_rows_are_one_sine_period():
    rows = l0_rows(DEFAULT_TIME, n_samples=4)
    assert rows == [
        ("2026-01-01T00:00:00.000", 1000),
        ("2026-01-01T00:00:01.000", 1100),
        ("2026-01-01T00:00:02.000", 1000),
        ("2026-01-01T00:00:03.000", 900),
    ]


def test_write_other_time(tmp_path):
    path = write_l0_file(
        tmp_path,
        time=datetime(2026, 3, 4, 5, 6, 7, tzinfo=UTC),
        version="1.0.0",
        n_samples=3,
    )
    assert path.name == "demo_craft_l0_20260304T050607_v1.0.0.csv"
    assert path.read_text().splitlines() == [
        "time,counts",
        "2026-03-04T05:06:07.000,1000",
        "2026-03-04T05:06:08.000,1087",
        "2026-03-04T05:06:09.000,913",
    ]
