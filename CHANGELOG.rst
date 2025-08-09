Changelog
=========

0.5.0
-----

- Add :ref:`block_level_ignore` and :ref:`page_level_ignore`
  `#33 <https://github.com/jdillard/sphinx-llms-txt/pull/33>`_
- Add :confval:`llms_txt_full_size_policy` configuration option to control behavior when :confval:`llms_txt_full_max_size` is exceeded.
  `#35 <https://github.com/jdillard/sphinx-llms-txt/pull/35>`_

0.4.1
-----

- Fix include paths and spacing
  `#31 <https://github.com/jdillard/sphinx-llms-txt/pull/31>`_

0.4.0
-----

- Add support for including source code files with :confval:`llms_txt_code_files` and :confval:`llms_txt_code_base_path` configuration options
  `#24 <https://github.com/jdillard/sphinx-llms-txt/pull/24>`_

0.3.2
-----

- Fix image paths to deployed images
  `#30 <https://github.com/jdillard/sphinx-llms-txt/pull/30>`_

0.3.1
-----

- Fix issue when ``source_suffix`` equals ``source_link_suffix``
  `#29 <https://github.com/jdillard/sphinx-llms-txt/pull/29>`_

0.3.0
-----

- Use first paragraph as default for ``llms_txt_summary``
  `#22 <https://github.com/jdillard/sphinx-llms-txt/pull/22>`_

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
