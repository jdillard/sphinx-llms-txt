Contributing
============

You will need to set up a development environment to make and test your changes before submitting them.

Local development
-----------------

#. Clone the `sphinx-llms-txt repository`_.

#. Create and activate a virtual environment:

   .. code-block:: console

      python3 -m venv .venv
      source .venv/bin/activate

#. Install development dependencies:

   .. code-block:: console

      pip install -e ".[dev]"

#. Install pre-commit Git hook scripts:

   .. code-block:: console

      pre-commit install

Testing changes
---------------

Run ``pytest`` before committing changes.

Current contributors
--------------------

Thanks to all who have contributed!
The people that have improved the code:

.. contributors:: jdillard/sphinx-llms-txt
   :avatars:
   :limit: 100
   :exclude: pre-commit-ci[bot],dependabot[bot]
   :order: ASC


.. _sphinx-llms-txt repository: https://github.com/jdillard/sphinx-llms-txt
