# Sphinx llms-full.txt Extension

A Sphinx extension that creates a single combined documentation `llms-full.txt` file, written in reStructuredText.

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

### `llms_txt_filename`

- **Type**: string
- **Default**: `'llms-full.txt'`
- **Description**: Name of the output file

### `llms_txt_verbose`

- **Type**: boolean  
- **Default**: `False`
- **Description**: Whether to include a summary in the build output

## License

MIT License - see LICENSE file for details.
