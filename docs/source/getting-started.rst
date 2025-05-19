Getting Started
===============

Demo
----

You can see this Sphinx project's `llms.txt`_ and `llms-full.txt`_ files as a simple example.

Installation
------------

Directly install via ``pip`` by using:

.. code-block:: bash

    pip install sphinx-llms-txt

Usage
-----

Add the extension to your Sphinx configuration (``conf.py``):

.. code-block:: python

    extensions = [
        'sphinx_llms_txt',
    ]

Once added, the extension will automatically generate the LLMs.txt files during the build process.

Features
--------

Sphinx LLMs.txt provides the following features:

- Creates ``llms.txt`` and ``llms-full.txt``
- Automatically add content from ``include`` directives
- Resolves relative paths in directives like ``image`` and ``figure`` to use full paths
   - Ability to add list of custom directives with ``llms_txt_directives``
   - Optionally, prepend a base URL using Sphinx's ``html_baseurl``
- Ability to exclude pages


.. _llms.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms.txt
.. _llms-full.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms-full.txt
