"""
This module provides readers for demo craft science files.
"""

from pathlib import Path

from astropy.table import Table

__all__ = ["read_file"]


def read_file(data_filename) -> Table:
    """
    Read a demo craft science file.

    Every demo craft product is a CSV file with a header row, so one reader
    serves all data levels.

    Parameters
    ----------
    data_filename : `str` or `~pathlib.Path`
        The file to read.

    Returns
    -------
    data : `~astropy.table.Table`
        The file contents, one column per CSV column.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is not a ``.csv`` file.
    """
    data_filename = Path(data_filename)
    if data_filename.suffix.lower() != ".csv":
        raise ValueError(f"{data_filename.name} is not a demo craft CSV file.")
    if not data_filename.exists():
        raise FileNotFoundError(f"{data_filename} does not exist.")
    return Table.read(data_filename, format="ascii.csv")
