Data directory
==============

This directory contains data files included with the package source
code distribution. Note that this is intended only for relatively small files
- large files should be externally hosted and downloaded as needed.
This directory is NOT for downloaded instrument data unless it is needed for testing purposes.

Calibration files
-----------------

Calibration files are stored in the ``calibration`` subdirectory. The demo
instrument has a single calibration file holding the gain and offset that turn
level 0 counts into level 1 flux.

Test files
----------

The ``test`` subdirectory holds one synthetic level 0 file,
``demo_craft_l0_20260101T000000_v0.0.1.csv``. The SDC processing Lambda runs
``process_file`` on every ``.csv`` file in this directory when
``USE_INSTRUMENT_TEST_DATA=True``. Regenerate it with::

    python -m demo_craft.util.synthetic demo_craft/data/test
