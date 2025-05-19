# Sphinx llms.txt generator

A Sphinx extension that generates a summary `llms.txt` file, written in Markdown, and a single combined documentation `llms-full.txt` file, written in reStructuredText.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-llms-txt.svg)](https://pypi.python.org/pypi/sphinx-llms-txt)
[![Downloads](https://static.pepy.tech/badge/sphinx-llms-txt/month)](https://pepy.tech/project/sphinx-llms-txt)

## Documentation

See [sphinx-llms-txt documentation](https://sphinx-llms-txt.readthedocs.io/en/latest/index.html) for installation and configuration instructions.

## Features

- Creates `llms.txt` and `llms-full.txt`
- Automatically add content from `include` directives
- Resolves relative paths in directives like `image` and `figure` to use full paths
  - Ability to add list of custom directives with `llms_txt_directives`
  - Optionally, prepend a base URL using Sphinx's `html_baseurl`
- Ability to exclude pages

## License

MIT License - see LICENSE file for details.
