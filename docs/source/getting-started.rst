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

Choosing an Output Format
-------------------------

By default, **sphinx-llms-txt** requires no additional configuration and links to raw reStructuredText source files in :confval:`_sources/ <sphinx:html_copy_source>`.
For optimal LLM support, you can use `sphinx-markdown-builder`_ and/or `sphinxcontrib-restbuilder`_, set up in parallel builds using CMake .

.. list-table:: Output Format Comparison
   :header-rows: 1
   :widths: 18 27 27 27

   * -
     - Default (no config)
     - Markdown (CMake)
     - RST (CMake)
   * - **Format**
     - Raw RST source
     - Rendered Markdown
     - Rendered RST
   * - **LLM Readability**
     - Good - preserves structure for simple syntax
     - Excellent - native LLM format
     - Good - Can provide more structured content
   * - **Key Advantage**
     - Zero setup required
     - More compact (less input tokens)
     - Can preserve Sphinx semantics
   * - **Key Disadvantage**
     - Raw directives (e.g., autodoc) won't be parsed
     - Loses structure from complex directives
     - Can lose structure from complex directives

See the project's `CMake setup <https://github.com/jdillard/sphinx-llms-txt/tree/main/cmake>`_ for an example of building HTML, Markdown, and RST in parallel.
Use :confval:`llms_txt_uri_template` to configure links to point to your preferred format.

See :doc:`advanced-configuration` for more information about how to use **sphinx-llms-txt**.


.. _sphinx-markdown-builder: https://pypi.org/project/sphinx-markdown-builder/
.. _sphinxcontrib-restbuilder: https://pypi.org/project/sphinxcontrib-restbuilder/

