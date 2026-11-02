"""
Science filename helpers for the demo craft instrument.

The SWxSOC convention for science file names is::

    {mission}_{inst}_{mode}_{level}{test}_{descriptor}_{time}_v{version}.{ext}

with ``time`` formatted as ``%Y%m%dT%H%M%S`` and ``mode``, ``test`` and
``descriptor`` optional. For this package that is, without the optional
parts, ``demo_craft_<level>_<YYYYmmddTHHMMSS>_v<X.Y.Z>.csv``.

.. todo::

    These helpers duplicate :func:`swxsoc.util.util.create_science_filename`
    and :func:`swxsoc.util.util.parse_science_filename` because the ``demo``
    mission in the shipped ``swxsoc`` configuration (``swxsoc/data/config.yml``)
    does not yet list a ``craft`` instrument, so the swxsoc helpers raise
    ``ValueError`` for every demo craft filename. Once that configuration lists
    ``craft`` (``instrument_package: demo_craft``) with a ``.csv`` file rule,
    this module can be reduced to thin wrappers around the swxsoc helpers.
"""

from datetime import UTC, datetime
from pathlib import Path

from astropy.time import Time

__all__ = [
    "MISSION_NAME",
    "INSTRUMENT_NAME",
    "FILE_EXTENSION",
    "TIME_FORMAT",
    "VALID_DATA_LEVELS",
    "create_science_filename",
    "parse_science_filename",
]

#: The mission this package belongs to.
MISSION_NAME = "demo"
#: The instrument this package processes data for.
INSTRUMENT_NAME = "craft"
#: The file extension of every demo craft science file.
FILE_EXTENSION = ".csv"
#: The ``strftime`` format of the time field in a science filename.
TIME_FORMAT = "%Y%m%dT%H%M%S"
#: The data levels this package recognises, lowest first.
VALID_DATA_LEVELS = ["raw", "l0", "ql", "l1", "l2", "l3"]


def _format_time(time) -> str:
    """Return a `~astropy.time.Time`, ISOT string or datetime as a filename field."""
    if isinstance(time, Time):
        return time.strftime(TIME_FORMAT)
    if isinstance(time, datetime):
        return time.strftime(TIME_FORMAT)
    return Time(time, format="isot").strftime(TIME_FORMAT)


def create_science_filename(
    instrument: str,
    time,
    level: str,
    version: str,
    mode: str = "",
    descriptor: str = "",
    test: bool = False,
) -> str:
    """
    Return a filename that follows the SWxSOC science filename convention.

    Parameters
    ----------
    instrument : `str`
        The instrument name. Must be ``"craft"``.
    time : `str` (ISOT) or `~astropy.time.Time` or `~datetime.datetime`
        The time of the first measurement in the file.
    level : `str`
        The data level. Must be one of `VALID_DATA_LEVELS`.
    version : `str`
        The file version, given as ``X.Y.Z``.
    mode : `str`, optional
        An optional instrument mode.
    descriptor : `str`, optional
        An optional product descriptor.
    test : `bool`, optional
        Whether the file is a test file.

    Returns
    -------
    filename : `str`
        The filename, including the ``.csv`` extension.

    Raises
    ------
    ValueError
        If the instrument, level, version, mode or descriptor is not valid.

    Examples
    --------
    >>> from demo_craft.util.filename import create_science_filename
    >>> create_science_filename("craft", "2026-01-01T00:00:00", "l1", "0.0.1")
    'demo_craft_l1_20260101T000000_v0.0.1.csv'
    """
    if instrument != INSTRUMENT_NAME:
        raise ValueError(
            f"Instrument, {instrument}, is not recognized. Must be {INSTRUMENT_NAME!r}."
        )
    if level not in VALID_DATA_LEVELS:
        raise ValueError(
            f"Level, {level}, is not recognized. Must be one of {VALID_DATA_LEVELS}."
        )
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(
            f"Version, {version}, is not formatted correctly. Should be X.Y.Z"
        )
    if "_" in mode or "_" in descriptor:
        raise ValueError(
            "The underscore symbol _ is not allowed in mode or descriptor."
        )

    test_str = "test" if test else ""
    fields = [
        MISSION_NAME,
        INSTRUMENT_NAME,
        mode,
        f"{level}{test_str}",
        descriptor,
        _format_time(time),
        f"v{version}",
    ]
    return "_".join(field for field in fields if field) + FILE_EXTENSION


def parse_science_filename(filepath) -> dict:
    """
    Parse a demo craft science filename into its constituent fields.

    Parameters
    ----------
    filepath : `str` or `~pathlib.Path`
        The filename, with or without a directory. The extension is ignored.

    Returns
    -------
    `dict`
        The keys ``mission``, ``instrument``, ``mode``, ``test``, ``time``,
        ``level``, ``version`` and ``descriptor``, with ``time`` as a
        `~astropy.time.Time`. Optional fields that are absent are `None`
        (``test`` is `False`).

    Raises
    ------
    ValueError
        If the filename is not for the ``demo`` mission and ``craft``
        instrument, or does not follow the convention.

    Examples
    --------
    >>> from demo_craft.util.filename import parse_science_filename
    >>> parsed = parse_science_filename("demo_craft_l0_20260101T000000_v0.0.1.csv")
    >>> parsed["mission"], parsed["instrument"], parsed["level"], parsed["version"]
    ('demo', 'craft', 'l0', '0.0.1')
    >>> parsed["time"].isot
    '2026-01-01T00:00:00.000'
    """
    stem = Path(filepath).stem
    components = stem.split("_")
    if len(components) < 5 or len(components) > 7:
        raise ValueError(
            f"{stem!r} does not follow the convention "
            "{mission}_{inst}_{mode}_{level}{test}_{descriptor}_{time}_v{version}"
        )
    mission, instrument = components[0], components[1]
    if mission != MISSION_NAME:
        raise ValueError(
            f"Not a valid mission name: {mission!r}. Expected: {MISSION_NAME!r}"
        )
    if instrument != INSTRUMENT_NAME:
        raise ValueError(
            f"Invalid instrument: {instrument!r}. Expected: {INSTRUMENT_NAME!r}"
        )

    version_field = components[-1]
    if not version_field.startswith("v"):
        raise ValueError(f"Missing version field in {stem!r}")
    version = version_field[1:]

    time_field = components[-2]
    try:
        parsed_time = datetime.strptime(time_field, TIME_FORMAT).replace(tzinfo=UTC)
    except ValueError as exc:
        raise ValueError(f"Invalid time {time_field!r} in {stem!r}") from exc

    # What remains between the instrument and the time is
    # [mode] level[test] [descriptor].
    middle = components[2:-2]
    mode = None
    descriptor = None
    if middle[0].replace("test", "") not in VALID_DATA_LEVELS:
        mode = middle.pop(0)
    if not middle:
        raise ValueError(f"Missing data level in {stem!r}")
    level_field = middle.pop(0)
    test = level_field.endswith("test")
    level = level_field.removesuffix("test")
    if level not in VALID_DATA_LEVELS:
        raise ValueError(
            f"Level, {level}, is not recognized. Must be one of {VALID_DATA_LEVELS}."
        )
    if middle:
        descriptor = middle.pop(0)
    if middle:
        raise ValueError(f"Too many fields in {stem!r}")

    return {
        "mission": mission,
        "instrument": instrument,
        "mode": mode,
        "test": test,
        "time": Time(parsed_time),
        "level": level,
        "version": version,
        "descriptor": descriptor,
    }
