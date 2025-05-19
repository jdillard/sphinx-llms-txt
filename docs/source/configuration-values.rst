Project Configuration Values
============================

.. confval:: llms_txt_full_file

   - **Type**: boolean
   - **Default**: ``True``
   - **Description**: Whether to write the single output file

   .. versionadded:: 0.1.0

.. confval:: llms_txt_full_filename

   - **Type**: string
   - **Default**: ``'llms-full.txt'``
   - **Description**: Name of the single output file

   .. versionadded:: 0.1.0

.. confval:: llms_txt_full_max_size

   - **Type**: integer or ``None``
   - **Default**: ``None`` (no limit)
   - **Description**: Sets a maximum line count for ``llms_txt_full_filename``.
     If exceeded, the file is skipped and a warning is shown, but the build still completes.

   .. versionadded:: 0.2.0

.. confval:: llms_txt_file

   - **Type**: boolean
   - **Default**: ``True``
   - **Description**: Whether to write the summary information file

   .. versionadded:: 0.2.0

.. confval:: llms_txt_filename

   - **Type**: string
   - **Default**: ``llms.txt``
   - **Description**: Name of the summary information file

   .. versionadded:: 0.2.0

.. confval:: llms_txt_directives

   - **Type**: list of strings
   - **Default**: ``[]`` (empty list)
   - **Description**: List of custom directive names to process for path resolution.

   .. versionadded:: 0.1.0

.. confval:: llms_txt_title

   - **Type**: string or ``None``
   - **Default**: ``None``
   - **Description**: Overrides the Sphinx project name as the heading in ``llms.txt``.

   .. versionadded:: 0.2.0

.. confval:: llms_txt_summary

   - **Type**: string or ``None``
   - **Default**: ``None``
   - **Description**: Optional, but recommended, summary description for ``llms.txt``.

   .. versionadded:: 0.2.0

.. confval:: llms_txt_exclude

   - **Type**: list of strings
   - **Default**: ``[]``
   - **Description**: A list of pages to ignore (e.g., ``["page1", "page_with_*"]``).

   .. versionadded:: 0.2.1

.. confval:: llms_txt_rm_directives

   - **Type**: boolean
   - **Default**: ``False``
   - **Description**: Whether to remove all directives from the output files.

   .. versionadded:: 0.2.3
