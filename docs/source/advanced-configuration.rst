Advanced Configuration
======================

This page covers advanced configuration options for the sphinx-llms-txt extension.

.. _customizing_llms_files:

Customizing the LLMs Files
^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the extension generates two files:

1. ``llms.txt`` - A summary file in Markdown format
2. ``llms-full.txt`` - A complete documentation file in reStructuredText format

You can customize these files in several ways:

.. _changing_filenames:

Changing Filenames
~~~~~~~~~~~~~~~~~~

You can change the default filenames by setting these values in your ``conf.py``:

.. code-block:: python

   llms_txt_filename = "custom-summary.txt"
   llms_txt_full_filename = "custom-docs.txt"

.. _disabling_file_generation:

Disabling File Generation
~~~~~~~~~~~~~~~~~~~~~~~~~

If you only want one of the files, you can disable generation of the other:

.. code-block:: python

   # Disable summary file
   llms_txt_file = False

   # Disable full documentation file
   llms_txt_full_file = False

.. _custom_summary:

Adding a Custom Summary
~~~~~~~~~~~~~~~~~~~~~~~

The summary file can include a custom description of your project:

.. code-block:: python

   llms_txt_summary = """
   This documentation explains how to use MyProject to build amazing
   applications. The project provides a comprehensive API for handling
   data processing and visualization.
   """

.. note:: The summary can span multiple lines and will be properly formatted in the output file.

.. _custom_title:

Custom Title
~~~~~~~~~~~~

By default, the project name from Sphinx is used as the title in ``llms.txt``. You can override this:

.. code-block:: python

   llms_txt_title = "My Custom Project Documentation"

.. _handling_large_documentation:

Handling Large Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For very large documentation sets, generating the full documentation file might exceed reasonable size limits.
You can set a maximum line count:

.. code-block:: python

   llms_txt_full_max_size = 10000  # Maximum 10,000 lines

If the generated file would exceed this limit, the extension will skip its generation and show a warning, allowing the build to complete.

.. tip:: Use :ref:`excluding_content` to remove less relevant pages.

.. _custom_directive_handling:

Custom Directive Handling
^^^^^^^^^^^^^^^^^^^^^^^^^

.. _path_resolution:

Path Resolution
~~~~~~~~~~~~~~~

The extension resolves paths in the common directives ``[ 'image', 'figure']`` by default.
You can add custom directives to this list:

.. code-block:: python

   llms_txt_directives = [
       "my-custom-image-directive",
       "another-directive-with-paths",
   ]

This ensures that paths in your custom directives are properly resolved in the generated files.

.. _excluding_content:

Excluding Content
^^^^^^^^^^^^^^^^^

You can exclude specific pages from being included in the generated files:

.. code-block:: python

   llms_txt_exclude = [
       "search",  # Exclude the search page
       "genindex",  # Exclude the index page
       "private_*",  # Exclude all pages starting with 'private_'
   ]

This is useful for excluding auto-generated pages, indexes, or content that isn't relevant for LLM consumption.

.. _using_html_baseurl:

Using HTML Base URL
^^^^^^^^^^^^^^^^^^^

If you want to include absolute URLs for resources in your documentation, you can use Sphinx's built-in ``html_baseurl`` configuration:

.. code-block:: python

   html_baseurl = "https://example.com/docs/"

When this option is set, all resolved paths in directives will be prefixed with this URL, creating absolute paths in the generated files.

.. _integration_examples:

Integration Examples
^^^^^^^^^^^^^^^^^^^^

Complete Configuration Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a complete example showing multiple :doc:`configuration-values`:

.. code-block:: python

   # File names and generation options
   llms_txt_filename = "ai-summary.txt"
   llms_txt_full_filename = "ai-full-docs.txt"
   llms_txt_full_max_size = 50000

   # Content customization
   llms_txt_title = "Project Documentation for AI Assistants"
   llms_txt_summary = """
   This is a comprehensive documentation set for our project.
   It includes API references, usage examples, and tutorials.
   """

   # Path handling
   html_baseurl = "https://docs.example.com/"
   llms_txt_directives = ["custom-image", "custom-include"]

   # Content filtering
   llms_txt_exclude = ["search", "genindex", "404", "private_*"]
