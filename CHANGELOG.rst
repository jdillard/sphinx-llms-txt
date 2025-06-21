Changelog
=========

0.2.4
-----

- Support source file suffix detection
  `#21 <https://github.com/jdillard/sphinx-llms-txt/pull/21>`_

0.2.3
-----

- Remove ``get_and_resolve_toctree`` method
  `#19 <https://github.com/jdillard/sphinx-llms-txt/pull/19>`_
- Simplify ``_sources`` lookup
  `#18 <https://github.com/jdillard/sphinx-llms-txt/pull/18>`_
- Add sphinx docs
  `#16 <https://github.com/jdillard/sphinx-llms-txt/pull/16>`_

0.2.2
-----

- Refactor LLMSFullManager with clearer class structure
- Add ``html_baseurl`` to **llms.txt** docs links
- Make glob pattern recursive

0.2.1
-----

- Add ability to exclude pages with ``llms_txt_exclude``

0.2.0
-----

- Add ``llms_txt_full_max_size`` configuration option to limit `llms-full.txt` file size
- Automatically add content from **include** directives in  **llms-full.txt**
- Add path resolution for a given set of directives  in **llms-full.txt**
- Add **llms.txt** file option, with ``llms_txt_title`` and ``llms_txt_summary`` config values

0.1.0
-----

- Initial release
