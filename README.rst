Machine Part Image Identifier
=============================

About
-----

This is a miniature library to process images containing a quarter and a
machine part. Once the part is located, various dimensions may be calculated.
For now only the height, width, and thread pitch are measured.

Example
-------

+----------+----------+
|  Input   |  Output  |
+==========+==========+
| |input|  | |output| |
+----------+----------+

.. |input| image:: ./figures/input.jpg
.. |output| image:: ./figures/output.jpg


Process
-------

+---------------------------------+----------+
|  Identify all contours in image | |step_0| |
+---------------------------------+----------+
| Combine overlapping contours    | |step_1| |
+---------------------------------+----------+
| Select largest contour and      |          |
| largest *square-like* contour   | |step_2| |
+---------------------------------+----------+
| Realign image based on largest  |          |
| contour angle                   | |step_3| |
+---------------------------------+----------+
| Draw dimensions and output      |          |
| calculations                    | |step_4| |
+---------------------------------+----------+

.. |step_0| image:: ./output/00_0.jpg
  :scale: 10 %
.. |step_1| image:: ./output/00_1.jpg
  :scale: 10 %
.. |step_2| image:: ./output/00_2.jpg
  :scale: 10 %
.. |step_3| image:: ./output/00_3.jpg
  :scale: 10 %
.. |step_4| image:: ./output/00_4.jpg
  :scale: 10 %


To run
------
.. code:: bash

  python2 main.py ./figures/input.jpg
