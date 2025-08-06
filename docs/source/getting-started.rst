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

See :doc:`advanced-configuration` for more information about how to use **sphinx-llms-txt**.

How It Works
------------

During the Sphinx build process:

1. **Content Collection**: Scans all of your documentation's ``_source`` pages and collects their content
2. **Directive Processing**: Resolves ``include`` directives by automatically incorporating their content
3. **Path Resolution**: Transforms relative paths in directives to full paths
4. **Output Generation**: Creates two optional files:

   - ``llms.txt``: A concise summary of your documentation, in Markdown
   - ``llms-full.txt``: A comprehensive version with all documentation content, in reStructuredText

5. **Content Filtering**: Allows you to exclude specific pages or sections using:

   - Configuration-based page exclusion patterns
   - Page-level metadata (`:llms-txt-ignore: true`)
   - Block-level ignore directives (`.. llms-txt-ignore-start/end`)


.. _llms.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms.txt
.. _llms-full.txt: https://sphinx-llms-txt.readthedocs.io/en/latest/llms-full.txt
