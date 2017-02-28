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

.. |input| image:: figures/input.jpg
  :scale: 15 %
.. |output| image:: figures/output.jpg
  :scale: 15 %


Process
-------

* Identify all contours in image
* Combine overlapping contours
* Select largest contour and largest *square-like* contour
* Realign image based on largest contour angle
* Draw dimensions and output calculations


To run
------
.. code:: bash

  ./main.py https://maneyko.com/partID/input.jpg
