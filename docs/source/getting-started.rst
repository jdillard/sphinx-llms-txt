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

How It Works
-----------

During the Sphinx build process:

1. **Content Collection**: Scans all of your documentation's ``_source`` pages and collects their content
2. **Directive Processing**: Resolves ``include`` directives by automatically incorporating their content
3. **Path Resolution**: Transforms relative paths in directives like ``image`` and ``figure`` to full paths
4. **Output Generation**: Creates two files:

   - ``llms.txt``: A concise summary of your documentation, in Markdown
   - ``llms-full.txt``: A comprehensive version with all documentation content, in reStructuredText

5. **Content Filtering**: Allows you to exclude specific pages from the generated files


.. _llms.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms.txt
.. _llms-full.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms-full.txt
