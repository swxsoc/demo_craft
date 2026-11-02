import pytest
from astropy.time import Time

from demo_craft.util.filename import (
    create_science_filename,
    parse_science_filename,
)

TIME = Time("2026-01-01T00:00:00")


def test_create_minimal():
    assert (
        create_science_filename("craft", TIME, "l1", "0.0.1")
        == "demo_craft_l1_20260101T000000_v0.0.1.csv"
    )


def test_create_accepts_isot_string():
    assert (
        create_science_filename("craft", "2026-01-01T00:00:00", "l0", "1.2.3")
        == "demo_craft_l0_20260101T000000_v1.2.3.csv"
    )


def test_create_with_optional_fields():
    name = create_science_filename(
        "craft", TIME, "l1", "0.0.1", mode="burst", descriptor="flux", test=True
    )
    assert name == "demo_craft_burst_l1test_flux_20260101T000000_v0.0.1.csv"
    parsed = parse_science_filename(name)
    assert parsed["mode"] == "burst"
    assert parsed["descriptor"] == "flux"
    assert parsed["test"] is True
    assert parsed["level"] == "l1"


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(instrument="eea", time=TIME, level="l1", version="0.0.1"),
        dict(instrument="craft", time=TIME, level="l9", version="0.0.1"),
        dict(instrument="craft", time=TIME, level="l1", version="1.0"),
        dict(instrument="craft", time=TIME, level="l1", version="a.b.c"),
        dict(instrument="craft", time=TIME, level="l1", version="0.0.1", mode="a_b"),
    ],
)
def test_create_rejects_invalid(kwargs):
    with pytest.raises(ValueError):
        create_science_filename(**kwargs)


def test_parse_roundtrip():
    for level in ["raw", "l0", "ql", "l1", "l2", "l3"]:
        name = create_science_filename("craft", TIME, level, "0.0.1")
        parsed = parse_science_filename(name)
        assert parsed["mission"] == "demo"
        assert parsed["instrument"] == "craft"
        assert parsed["level"] == level
        assert parsed["version"] == "0.0.1"
        assert parsed["time"] == TIME
        assert parsed["mode"] is None
        assert parsed["descriptor"] is None
        assert parsed["test"] is False


def test_parse_ignores_directory_and_extension(tmp_path):
    parsed = parse_science_filename(
        tmp_path / "demo_craft_l0_20260101T000000_v0.0.1.cdf"
    )
    assert parsed["level"] == "l0"


@pytest.mark.parametrize(
    "name",
    [
        "hermes_craft_l0_20260101T000000_v0.0.1.csv",
        "demo_eea_l0_20260101T000000_v0.0.1.csv",
        "demo_craft_l0_20260101_v0.0.1.csv",
        "demo_craft_l0_20260101T000000_0.0.1.csv",
        "demo_craft_20260101T000000_v0.0.1.csv",
        "demo_craft_a_b_c_l0_20260101T000000_v0.0.1.csv",
        "demo_craft.csv",
    ],
)
def test_parse_rejects_invalid(name):
    with pytest.raises(ValueError):
        parse_science_filename(name)


def test_matches_swxsoc_parser_once_config_lists_craft():
    """
    The local helpers exist only because the swxsoc demo configuration does
    not yet list a craft instrument. Once it does, swxsoc's parser must agree
    with ours; until then this test is skipped rather than failed.
    """
    from swxsoc.util import util as swxsoc_util

    name = create_science_filename("craft", TIME, "l1", "0.0.1")
    try:
        theirs = swxsoc_util.parse_science_filename(name)
    except ValueError:
        pytest.skip("swxsoc demo config does not list craft yet")
    ours = parse_science_filename(name)
    assert theirs["instrument"] == ours["instrument"]
    assert theirs["level"] == ours["level"]
    assert theirs["time"] == ours["time"]
