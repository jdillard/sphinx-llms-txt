# Sphinx llms.txt generator

A Sphinx extension that generates a summary `llms.txt` file, written in Markdown, and a single combined documentation `llms-full.txt` file, written in reStructuredText.

[![PyPI version](https://img.shields.io/pypi/v/sphinx-llms-txt.svg)](https://pypi.python.org/pypi/sphinx-llms-txt)
[![Downloads](https://static.pepy.tech/badge/sphinx-llms-txt/month)](https://pepy.tech/project/sphinx-llms-txt)

## Installation

```bash
pip install sphinx-llms-txt
```

## Usage

1. Add the extension to your Sphinx configuration (`conf.py`):

```python
extensions = [
    'sphinx_llms_txt',
]
```

## Configuration Options

### `llms_txt_full_file`

- **Type**: boolean
- **Default**: `'True'`
- **Description**: Whether to write the single output file

### `llms_txt_full_filename`

- **Type**: string
- **Default**: `'llms-full.txt'`
- **Description**: Name of the single output file

### `llms_txt_full_max_size`

- **Type**: integer or `None`
- **Default**: `None` (no limit)
- **Description**: Sets a maximum line count for `llms_txt_full_filename`.
  If exceeded, the file is skipped and a warning is shown, but the build still completes.

### `llms_txt_file`

- **Type**: boolean
- **Default**: `True`
- **Description**: Whether to write the summary information file

### `llms_txt_filename`

- **Type**: string
- **Default**: `llms.txt`
- **Description**: Name of the summary information file

### `llms_txt_directives`

- **Type**: list of strings
- **Default**: `[]`
- **Description**: List of custom directive names to process for path resolution.

### `llms_txt_title`

- **Type**: string or `None`
- **Default**: `None`
- **Description**: Overrides the Sphinx project name as the heading in `llms.txt`.

### `llms_txt_summary`

- **Type**: string or `None`
- **Default**: `None`
- **Description**: Optional, but recommended, summary description for `llms.txt`.

### `llms_txt_exclude`

- **Type**: list of strings
- **Default**: `[]`
- **Description**: A list of pages to ignore  (e.g., `["page1", "page_with_*"]`).

## Features

- Creates `llms.txt` and `llms-full.txt`
- Automatically add content from `include` directives
- Resolves relative paths in directives like `image` and `figure` to use full paths
  - Ability to add list of custom directives with `llms_txt_directives`
  - Optionally, prepend a base URL using Sphinx's `html_baseurl`
- Ability to exclude pages

## License

MIT License - see LICENSE file for details.
