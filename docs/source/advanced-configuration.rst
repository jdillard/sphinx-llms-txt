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
You can set a maximum line count and control what happens when that limit is exceeded:

.. code-block:: python

   llms_txt_full_max_size = 10000  # Maximum 10,000 lines
   llms_txt_full_size_policy = "warn_skip"  # Default behavior

The ``llms_txt_full_size_policy`` setting controls both the log level and action taken when the size limit is exceeded.
It uses the format ``"<loglevel>_<action>"``:

**Log levels:**
- ``warn``: Log as a warning (default)
- ``info``: Log as informational message

**Actions:**
- ``skip``: Don't create the file (default)
- ``keep``: Create the file anyway, ignoring the size limit
- ``note``: Create a placeholder file explaining why the full file wasn't generated

.. tip:: Use :ref:`excluding_content` to remove less relevant pages and reduce the file size.

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

There are several ways to exclude content from the generated ``llms-full.txt`` file:

.. _global_exclusion:

Global Page Exclusion
~~~~~~~~~~~~~~~~~~~~~~

You can exclude specific pages from being included in the generated files:

.. code-block:: python

   llms_txt_exclude = [
       "search",  # Exclude the search page
       "genindex",  # Exclude the index page
       "private_*",  # Exclude all pages starting with 'private_'
   ]

This is useful for excluding auto-generated pages, indexes, or content that isn't relevant for LLM consumption.
It can also be used to reduce the size of llms-full.txt.

.. _page_level_ignore:

Page-Level Ignore Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can exclude individual pages by adding metadata at the top of any reStructuredText file:

.. code-block:: restructuredtext

   :llms-txt-ignore: true

   Page Title
   ==========

   This entire page will be excluded from llms-full.txt

When this metadata is present, the entire page is skipped during processing.

.. _block_level_ignore:

Block-Level Ignore Directives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can exclude specific sections within a page using ignore directives:

.. code-block:: restructuredtext

   Page Title
   ==========

   This content will be included in llms-full.txt.

   .. llms-txt-ignore-start

   This content will be excluded from llms-full.txt.

   Section To Ignore
   -----------------

   This entire section and any nested content will be ignored.

   .. code-block:: python

      # This code block will also be ignored
      def ignored_function():
          pass

   .. llms-txt-ignore-end

   This content will be included again.

Block-level ignores can be useful for:

- Removing internal notes or TODOs
- Hiding implementation details while keeping user-facing documentation

.. note::
   - Multiple ignore blocks can be used within the same file
   - Ignore directives work with any indentation level

.. _including_code_files:

Including Source Code Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can include source code files from your project at the end of :confval:`llms_txt_full_filename`.

Use include/exclude syntax to precisely control which files are included:

.. code-block:: python

   llms_txt_code_files = [
       "+:src/**/*.py",           # Include all Python files in src
       "-:src/**/__pycache__/**", # Exclude Python cache files
   ]

Pattern syntax:

- **+:pattern**: Include files matching the pattern. Processed first to collect matching files.
- **-:pattern**: Exclude files matching the pattern. Applied to filter out unwanted files.

Code files are processed as follows:

- **Glob patterns**: Use standard glob patterns (``*``, ``**``, ``?``) to match files
- **Relative paths**: Patterns are resolved relative to your Sphinx source directory
- **Formatting**: Each file is presented with a title and syntax-highlighted code block

.. _customizing_code_paths:

Customizing Code File Paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the extension automatically detects the relative path from your Sphinx source directory to the git root and strips that prefix from displayed file paths. You can customize this behavior:

.. code-block:: python

   # Manually specify base path to strip
   llms_txt_code_base_path = "../../"

   # Disable path stripping entirely
   llms_txt_code_base_path = ""

This helps create cleaner, more readable file paths in the generated documentation.

.. _using_html_baseurl:

Using HTML Base URL
^^^^^^^^^^^^^^^^^^^

If you want to include absolute URLs for resources in your documentation, you can use Sphinx's built-in ``html_baseurl`` configuration:

.. code-block:: python

   html_baseurl = "https://example.com/docs/"

When this option is set, all resolved paths in directives will be prefixed with this URL, creating absolute paths in the generated files.

.. _customizing_uri_links:

Customizing URI Links in llms.txt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the ``llms.txt`` file links to source files in the ``_sources`` directory when available, falling back to HTML pages when sources aren't available.
You can customize this behavior using URI templates with :confval:`llms_txt_uri_template`:

.. code-block:: python

   # Default: Link to source files, if _sources exists
   llms_txt_uri_template = "{base_url}_sources/{docname}{suffix}{sourcelink_suffix}"

   # Default: Link to HTML pages instead, if _sources doesn't exist
   llms_txt_uri_template = "{base_url}{docname}.html"

   # Manual: Link to a custom markdown build
   llms_txt_uri_template = "{base_url}{docname}.md"

.. _available_template_variables:

Available Template Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your URI template can use the following variables:

- ``{base_url}`` - The base URL from ``html_baseurl`` configuration (includes trailing slash)
- ``{docname}`` - The document name (e.g., ``index``, ``guide/intro``)
- ``{suffix}`` - The source file suffix (e.g., ``.rst``, ``.md``) - may be empty if no source file exists
- ``{sourcelink_suffix}`` - The suffix from ``html_sourcelink_suffix`` configuration (e.g., ``.txt``)

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
   llms_txt_full_size_policy = "warn_note"

   # Content customization
   llms_txt_title = "Project Documentation for AI Assistants"
   llms_txt_summary = """
   This is a comprehensive documentation set for our project.
   It includes API references, usage examples, and tutorials.
   """
   llms_txt_uri_template = "{base_url}{docname}.md"

   # Path handling
   html_baseurl = "https://docs.example.com/"
   llms_txt_directives = ["custom-image", "custom-include"]

   # Content filtering
   llms_txt_exclude = ["search", "genindex", "404", "private_*"]

   # Source code inclusion with include/exclude patterns
   llms_txt_code_files = [
       "+:../../src/**/*.py",           # Include Python files
       "+:../../config/*.yaml",         # Include config files
       "-:../../src/**/__pycache__/**", # Exclude cache files
   ]
   llms_txt_code_base_path = "../../"
