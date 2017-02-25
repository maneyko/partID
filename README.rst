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


Installation
------------
.. code:: bash

  git clone https://github.com/maneyko/class.git
  mkdir images
  mv img/path/{image_name}.{jpg,png} images/


To run
------
.. code:: bash

  ./main.py ./images/{image_name}.{jpg,png}


Output
------

Output images will be in ``./output/``