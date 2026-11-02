import shutil

import pytest

import demo_craft.calibration as calib
from demo_craft import _test_files_directory
from demo_craft.io.file_tools import read_file
from demo_craft.util.filename import parse_science_filename

L0_NAME = "demo_craft_l0_20260101T000000_v0.0.1.csv"


@pytest.fixture
def l0_file(tmp_path):
    """A copy of the bundled level 0 test file in a scratch directory."""
    return shutil.copy(_test_files_directory / L0_NAME, tmp_path / L0_NAME)


def test_bundled_test_data_exists():
    assert (_test_files_directory / L0_NAME).is_file()


def test_process_file_l0_yields_one_l1(l0_file, tmp_path):
    outputs = calib.process_file(l0_file)

    assert len(outputs) == 1
    (l1_file,) = outputs
    assert l1_file.is_file()
    assert l1_file.parent == tmp_path
    parsed = parse_science_filename(l1_file)
    assert parsed["mission"] == "demo"
    assert parsed["instrument"] == "craft"
    assert parsed["level"] == "l1"
    assert parsed["time"] == parse_science_filename(l0_file)["time"]
    assert l1_file.name == "demo_craft_l1_20260101T000000_v0.0.1.csv"


def test_l1_contents(l0_file):
    (l1_file,) = calib.process_file(l0_file)
    l0 = read_file(l0_file)
    l1 = read_file(l1_file)

    assert l1.colnames == ["time", "counts", "flux"]
    assert len(l1) == len(l0) == 60
    assert list(l1["counts"]) == list(l0["counts"])
    # gain 0.25, offset -12.5 from the bundled calibration file
    assert l1["flux"][0] == pytest.approx(0.25 * 1000 - 12.5)


def test_process_file_honours_output_path(l0_file, tmp_path):
    out_dir = tmp_path / "out"
    (l1_file,) = calib.process_file(l0_file, output_path=out_dir)
    assert l1_file.parent == out_dir
    assert l1_file.is_file()


def test_process_file_writes_to_tempdir_in_lambda(l0_file, tmp_path, monkeypatch):
    import tempfile

    lambda_tmp = tmp_path / "lambda_tmp"
    lambda_tmp.mkdir()
    monkeypatch.setenv("LAMBDA_ENVIRONMENT", "DEVELOPMENT")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(lambda_tmp))

    (l1_file,) = calib.process_file(l0_file)
    assert l1_file.parent == lambda_tmp


def test_process_file_raw_is_treated_like_l0(l0_file, tmp_path):
    raw_file = l0_file.rename(tmp_path / L0_NAME.replace("_l0_", "_raw_"))
    (l1_file,) = calib.process_file(raw_file)
    assert parse_science_filename(l1_file)["level"] == "l1"


@pytest.mark.parametrize("level", ["l1", "ql", "l2", "l3"])
def test_process_file_higher_levels_stop_the_chain(level, tmp_path):
    name = L0_NAME.replace("_l0_", f"_{level}_")
    assert calib.process_file(tmp_path / name) == []


@pytest.mark.parametrize(
    "name",
    [
        "hermes_eea_l0_20260101T000000_v0.0.1.csv",  # other mission
        "demo_myinst_l0_20260101T000000_v0.0.1.csv",  # other instrument
        "padre_craft_l0_20260101T000000_v0.0.1.csv",  # craft of another mission
        "not_a_science_file.csv",
    ],
)
def test_process_file_rejects_foreign_filenames(name, tmp_path):
    with pytest.raises(ValueError):
        calib.process_file(tmp_path / name)


def test_process_file_rejects_non_csv(l0_file):
    cdf_name = l0_file.with_suffix(".cdf")
    l0_file.rename(cdf_name)
    with pytest.raises(ValueError):
        calib.process_file(cdf_name)


def test_process_file_missing_input(tmp_path):
    with pytest.raises(FileNotFoundError):
        calib.process_file(tmp_path / L0_NAME)


def test_calibrate_file_rejects_l1(tmp_path):
    with pytest.raises(ValueError) as excinfo:
        calib.calibrate_file(tmp_path / L0_NAME.replace("_l0_", "_l1_"))
    assert "expected one of" in str(excinfo.value)


def test_get_calibration_file():
    calib_file = calib.get_calibration_file("2026-01-01T00:00:00")
    assert calib_file is not None
    assert calib_file.is_file()


def test_read_calibration_file():
    calibration = calib.read_calibration_file(calib.get_calibration_file(None))
    assert calibration == {"gain": 0.25, "offset": -12.5}


def test_read_calibration_file_rejects_bad_file(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("gain\n1\n")
    with pytest.raises(ValueError):
        calib.read_calibration_file(bad)
