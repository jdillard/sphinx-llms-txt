Sphinx llms.txt Generator
=========================

A `Sphinx`_ extension that generates a summary ``llms.txt`` file, written in Markdown, and a single combined documentation ``llms-full.txt`` file, written in reStructuredText.

|PyPI version| |Conda Version| |Downloads| |Parallel Safe| |GitHub Stars|

Demo
----

You can see this Sphinx project's `llms.txt`_ and `llms-full.txt`_ files as an example of the default :ref:`output formats <choosing-output-format>`.

Alternative :ref:`output formats <choosing-output-format>` are also available: `llms.md.txt`_ (Markdown) and `llms.rst.txt`_ (reStructuredText).

Highlights
----------

**Zero Configuration**
   Add the extension to your ``conf.py`` and you're done.
   The extension automatically collects your documentation and generates both ``llms.txt`` and ``llms-full.txt`` during your normal Sphinx build.

**Intelligent Content Processing**
   Automatically resolves ``include`` directives, transforms relative paths, and handles your documentation structure without manual intervention.

**Customizable When Needed**
   Filter content, include source code files, or integrate with alternative output formats like Markdown for even better LLM compatibility.
   See :doc:`getting-started` for output format options and :doc:`configuration-values` for all settings.

.. toctree::
   :maxdepth: 2

   getting-started
   advanced-configuration
   configuration-values
   contributing
   changelog


.. _llms.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms.txt
.. _llms-full.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms-full.txt
.. _llms.md.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms.md.txt
.. _llms.rst.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms.rst.txt
.. _Sphinx: http://sphinx-doc.org/

.. |PyPI version| image:: https://img.shields.io/pypi/v/sphinx-llms-txt.svg
   :target: https://pypi.python.org/pypi/sphinx-llms-txt
   :alt: Latest PyPi Version
.. |Conda Version| image:: https://img.shields.io/conda/vn/conda-forge/sphinx-llms-txt.svg
    :target: https://anaconda.org/conda-forge/sphinx-llms-txt
    :alt: Latest Conda Version
.. |Downloads| image:: https://static.pepy.tech/badge/sphinx-llms-txt/month
    :target: https://pepy.tech/project/sphinx-llms-txt
    :alt: PyPi Downloads per month
.. |Parallel Safe| image:: https://img.shields.io/badge/parallel%20safe-true-brightgreen
   :target: #
   :alt: Parallel read/write safe
.. |GitHub Stars| image:: https://img.shields.io/github/stars/jdillard/sphinx-llms-txt?style=social
   :target: https://github.com/jdillard/sphinx-llms-txt
   :alt: GitHub Repository stars
