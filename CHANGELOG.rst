********
Releases
********

Notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`__.

0.0.1 (2026-11-02)
==================

Added
-----

* ``demo_craft.calibration.process_file``, which turns one level 0 (or raw)
  CSV file into one level 1 CSV file and returns nothing for level 1 and
  higher, so the SDC pipeline chain stops after one step.
* Local science filename helpers in ``demo_craft.util.filename`` that follow
  the SWxSOC convention, pending a ``craft`` entry for the demo mission in the
  ``swxsoc`` configuration.
* A synthetic level 0 test file under ``demo_craft/data/test`` and the
  generator ``demo_craft.util.synthetic`` that reproduces it.
