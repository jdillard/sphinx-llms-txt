Sphinx llms.txt Generator
=========================

A `Sphinx`_ extension that generates a summary ``llms.txt`` file, written in Markdown, and a single combined documentation ``llms-full.txt`` file, written in reStructuredText.

|PyPI version|

.. toctree::
   :maxdepth: 2

   getting-started
   configuration-values
   contributing
   changelog

Features
--------

Sphinx LLMs.txt provides the following features:

- Creates ``llms.txt`` and ``llms-full.txt``
- Automatically add content from ``include`` directives
- Resolves relative paths in directives like ``image`` and ``figure`` to use full paths
   - Ability to add list of custom directives with ``llms_txt_directives``
   - Optionally, prepend a base URL using Sphinx's ``html_baseurl``
- Ability to exclude pages


.. _Sphinx: http://sphinx-doc.org/

.. |PyPI version| image:: https://img.shields.io/pypi/v/sphinx-llms-txt.svg
   :target: https://pypi.python.org/pypi/sphinx-llms-txt
   :alt: Latest PyPi Version
