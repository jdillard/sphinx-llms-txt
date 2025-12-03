Getting Started
===============

Installation
------------

Directly install by using:

.. tab:: via pip

   .. code-block:: bash

      pip install sphinx-llms-txt

.. tab:: via conda:

   .. code-block:: bash

      conda install -c conda-forge sphinx-llms-txt

Usage
-----

Add the extension to your Sphinx configuration (``conf.py``):

.. code-block:: python

    extensions = [
        'sphinx_llms_txt',
    ]

After the HTML finishes building, **sphinx-llms-txt** will output the location of the output files::

    sphinx-llms-txt: Created /path/to/_build/html/llms-full.txt with 45 sources and 6879 lines
    sphinx-llms-txt: created /path/to/_build/html/llms.txt


.. tip:: Make sure to confirm the accuracy of the output files after installs and upgrades.

See :doc:`advanced-configuration` for more information about how to use **sphinx-llms-txt**.
