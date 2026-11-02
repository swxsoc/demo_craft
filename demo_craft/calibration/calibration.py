"""
A module for all things calibration.

The demo craft processing chain is deliberately short: one level 0 file is
turned into one level 1 file, and level 1 files (and anything higher) are
left alone, so the shared SDC pipeline sees exactly one processed output per
upload.
"""

import os
import tempfile
from pathlib import Path

from astropy.time import Time

from demo_craft import _data_directory, log
from demo_craft.io.file_tools import read_file
from demo_craft.util.filename import (
    FILE_EXTENSION,
    INSTRUMENT_NAME,
    create_science_filename,
    parse_science_filename,
)

__all__ = [
    "process_file",
    "calibrate_file",
    "get_calibration_file",
    "read_calibration_file",
]

#: Data levels that `process_file` turns into a level 1 product.
INPUT_LEVELS = ("raw", "l0")
#: Version written into every level 1 filename.
L1_VERSION = "0.0.1"


def process_file(
    data_filename: Path, output_path: Path | None = None
) -> list[Path | None]:
    """
    This is the entry point for the pipeline processing.
    It runs all of the various processing steps required.

    A level 0 (or raw) file produces exactly one level 1 file. A level 1 or
    higher file produces nothing, which ends the processing chain.

    Parameters
    ----------
    data_filename: Path
        Fully specificied filename of an input file
    output_path: Path, optional
        Directory to write output files into. When not given, files are
        written next to the input file, or into the system temporary
        directory when ``LAMBDA_ENVIRONMENT`` is set, which is where the
        SDC processing Lambda uploads outputs from.

    Returns
    -------
    output_files: list[Path | None]
        Fully specificied filenames for the output files.

    Raises
    ------
    ValueError
        If the filename is not a demo craft science filename or the file is
        not a ``.csv`` file. The processing Lambda treats this as "skip".
    FileNotFoundError
        If the input file does not exist.

    Notes
    -----
    If you want to have the pipeline mark files as processes, but don't want to
    return an output file, return a list with None element.
    If you don't want to mark the file as processed, return an empty list.
    """
    data_filename = Path(data_filename)
    log.info(f"Processing file {data_filename}.")
    output_files = []

    parsed = parse_science_filename(data_filename)
    if parsed["level"] not in INPUT_LEVELS:
        log.info(
            f"{data_filename.name} is level {parsed['level']}; "
            "nothing further to produce."
        )
        return output_files
    if data_filename.suffix.lower() != FILE_EXTENSION:
        raise ValueError(
            f"{data_filename.name} is not a {FILE_EXTENSION} file; "
            "demo craft only processes CSV level 0 files."
        )

    if output_path is None:
        if os.getenv("LAMBDA_ENVIRONMENT"):
            output_path = Path(tempfile.gettempdir())
        else:
            output_path = data_filename.parent

    calibrated_file = calibrate_file(data_filename, output_path=output_path)
    output_files.append(calibrated_file)

    # add other tasks below
    return output_files


def calibrate_file(data_filename: Path, output_path: Path | None = None) -> Path:
    """
    Given a level 0 file, calibrate it and return the new level 1 file.

    The level 1 file keeps the ``time`` and ``counts`` columns of the input
    and adds ``flux``, the counts converted with the gain and offset from the
    calibration file.

    Parameters
    ----------
    data_filename: Path
        Fully specificied filename of the level 0 file
    output_path: Path, optional
        Directory to write the level 1 file into. Defaults to the directory
        of the input file.

    Returns
    -------
    output_filename: Path
        Fully specificied filename of the level 1 file

    Raises
    ------
    ValueError
        If the calibration file for the input's time cannot be found, or the
        filename is not a demo craft level 0 filename.

    Examples
    --------
    >>> from demo_craft import _test_files_directory
    >>> from demo_craft.calibration import calibrate_file
    >>> import tempfile
    >>> l0_file = _test_files_directory / "demo_craft_l0_20260101T000000_v0.0.1.csv"
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     calibrate_file(l0_file, output_path=tmp).name
    'demo_craft_l1_20260101T000000_v0.0.1.csv'
    """
    data_filename = Path(data_filename)
    parsed = parse_science_filename(data_filename)
    if parsed["level"] not in INPUT_LEVELS:
        raise ValueError(
            f"{data_filename.name} is level {parsed['level']}, "
            f"expected one of {INPUT_LEVELS}."
        )

    calib_file = get_calibration_file(parsed["time"])
    if calib_file is None:
        raise ValueError(f"Calibration file for {data_filename} not found.")
    calib_data = read_calibration_file(calib_file)

    data = read_file(data_filename)
    data["flux"] = calib_data["gain"] * data["counts"] + calib_data["offset"]
    log.info(f"Calibrated {len(data)} samples from {data_filename.name}.")

    output_dir = Path(output_path) if output_path is not None else data_filename.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = output_dir / create_science_filename(
        instrument=INSTRUMENT_NAME,
        time=parsed["time"],
        level="l1",
        version=L1_VERSION,
    )
    data.write(output_filename, format="ascii.csv", overwrite=True)
    log.info(f"Wrote {output_filename}.")
    return output_filename


def get_calibration_file(time: Time) -> Path | None:
    """
    Given a time, return the appropriate calibration file.

    The demo instrument has a single calibration that applies at all times.

    Parameters
    ----------
    time: ~astropy.time.Time
        The time of the data to be calibrated.

    Returns
    -------
    calib_filename: Path or None
        Fully specificied filename for the appropriate calibration file, or
        None if there is none.

    Examples
    --------
    >>> from demo_craft.calibration import get_calibration_file
    >>> get_calibration_file("2026-01-01T00:00:00").name
    'demo_craft_calibration_v0.0.1.csv'
    """
    calib_filename = (
        _data_directory / "calibration" / "demo_craft_calibration_v0.0.1.csv"
    )
    if not calib_filename.exists():
        return None
    return calib_filename


def read_calibration_file(calib_filename: Path) -> dict:
    """
    Given a calibration file, return the calibration structure.

    Parameters
    ----------
    calib_filename: Path
        Fully specificied filename of the calibration file

    Returns
    -------
    calibration: dict
        The keys ``gain`` and ``offset`` as floats.

    Raises
    ------
    FileNotFoundError
        If the calibration file does not exist.
    ValueError
        If the calibration file does not hold a gain and an offset.
    """
    table = read_file(calib_filename)
    if {"gain", "offset"} - set(table.colnames) or len(table) != 1:
        raise ValueError(
            f"{Path(calib_filename).name} must have one row with gain and offset."
        )
    return {"gain": float(table["gain"][0]), "offset": float(table["offset"][0])}
