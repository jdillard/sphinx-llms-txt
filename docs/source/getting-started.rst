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

.. _choosing-output-format:

Choosing an Output Format
-------------------------

By default, **sphinx-llms-txt** requires no additional configuration and links to raw reStructuredText source files created by the HTML builder.
For optimal LLM support, see the alternative builders below and the :ref:`CMake workflow <cmake_workflow>` for setup.

.. list-table:: Output Format Comparison
   :header-rows: 1
   :widths: 18 27 27 27

   * -
     - Default
     - Markdown
     - reStructuredText
   * - **Setup**
     - No config
     - CMake [#sphinxllm]_
     - CMake
   * - **Builder**
     - Native [#native]_
     - `sphinx-markdown-builder`_
     - `sphinxcontrib-restbuilder`_
   * - **Format**
     - Raw reStructuredText source
     - Rendered Markdown [#rendered]_
     - Rendered reStructuredText [#rendered]_
   * - **LLM Readability**
     - Good - preserves structure for simple syntax
     - Excellent - native LLM format
     - Good - Can provide more structured content
   * - **Key Advantage**
     - Zero setup required
     - More compact (less input tokens)
     - Can preserve Sphinx semantics
   * - **Key Disadvantage**
     - Raw directives won't be parsed [#autodoc]_
     - Loses structure from complex directives
     - Can lose structure from complex directives
   * - **llms-full.txt support**
     - Supported with above caveats
     - Pending `support <https://github.com/liran-funaro/sphinx-markdown-builder/pull/37>`__ [#pending]_
     - Pending `support <https://github.com/sphinx-contrib/restbuilder/pull/35>`__ [#pending]_

.. _sphinx-markdown-builder: https://pypi.org/project/sphinx-markdown-builder/
.. _sphinxcontrib-restbuilder: https://pypi.org/project/sphinxcontrib-restbuilder/

.. rubric:: Footnotes

.. [#sphinxllm] See `sphinx-llm <https://github.com/jacobtomlinson/sphinx-llm>`_ for CMake-free Markdown builds, note it may double build times due to serial execution.
.. [#native] Uses raw :confval:`_sources/ <sphinx:html_copy_source>` files created by Sphinx's HTML builder with some minor enhancements.
.. [#autodoc] Directives like ``autodoc`` will appear as raw directive syntax rather than the extracted docstrings.
.. [#pending] PRs that add ``llms-full.txt`` concatenation support have yet to be released.
.. [#rendered] Directives are expanded and processed before output, so content like autodoc docstrings will be included.

