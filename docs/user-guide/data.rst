.. _data:

****
Data
****

Overview
========

The demo mission has no real instrument. Its data products exist to exercise
the shared SDC pipeline, so they are small CSV files that any tool can read.

Data Description
----------------

+----------+--------------------------------------------------+------------------------------------------------+
| Level    | Product                                          | Description                                    |
+==========+==================================================+================================================+
| 0        | ``demo_craft_l0_<time>_v<version>.csv``          | ``time`` (ISOT) and integer ``counts``, one    |
|          |                                                  | row per second; synthetic, see                 |
|          |                                                  | `demo_craft.util.synthetic`.                   |
+----------+--------------------------------------------------+------------------------------------------------+
| 1        | ``demo_craft_l1_<time>_v0.0.1.csv``              | The level 0 rows plus ``flux``, the counts     |
|          |                                                  | converted with the bundled gain and offset.    |
+----------+--------------------------------------------------+------------------------------------------------+

Getting Data
============

One level 0 file ships with the package in ``demo_craft/data/test``; any
other can be generated with `demo_craft.util.synthetic.write_l0_file`.

Reading Data
============

`demo_craft.io.file_tools.read_file` reads any level into an
`astropy.table.Table`.

Calibrating Data
================

`demo_craft.calibration.calibration.process_file` turns a level 0 file into a
level 1 file and stops there; level 1 and higher files are returned unchanged
(an empty output list) so the pipeline chain ends after one step.
