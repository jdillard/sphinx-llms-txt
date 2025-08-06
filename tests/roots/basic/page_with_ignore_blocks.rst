Page With Ignore Blocks
=======================

This content should appear in llms-full.txt.

.. llms-txt-ignore-start

This content should be ignored and not appear in llms-full.txt.

Section Ignored
---------------

This section should also be ignored.

.. llms-txt-ignore-end

This content after the ignore block should appear in llms-full.txt.

Another Section
---------------

This content should definitely appear.

.. llms-txt-ignore-start

Another ignored block with multiple lines.

- Item 1 (ignored)
- Item 2 (ignored)

.. code-block:: python

   # This code should be ignored
   def ignored_function():
       pass

.. llms-txt-ignore-end

Final content that should appear.