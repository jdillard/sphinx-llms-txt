"""Integration tests for sphinx-llms-txt."""

import sys
from pathlib import Path
from sphinx.testing.util import _clean_up_global_state


def test_build_html_with_llms_txt(basic_sphinx_app):
    """Test building HTML documentation with llms-txt enabled."""
    app = basic_sphinx_app
    app.build()

    # Check if the output file was created
    output_file = Path(app.outdir) / "test-llms-full.txt"
    assert output_file.exists(), f"Output file {output_file} does not exist"

    # Read the content of the output file
    content = output_file.read_text()

    # Check that content from all pages is included
    assert "Welcome to Test Project's documentation!" in content
    assert "Page 1 Title" in content
    assert "Page 2 Title" in content
    assert "Content for section 1" in content
    assert "Content for section A" in content


def test_custom_filename(temp_dir, rootdir):
    """Test using a custom filename for the output."""
    from sphinx.testing.util import SphinxTestApp

    src_dir = rootdir / "basic"

    # Create a copy of the configuration with a different filename
    custom_conf = src_dir / "conf_custom.py"
    with open(src_dir / "conf.py") as f:
        conf_content = f.read()

    conf_content = conf_content.replace(
        'llms_txt_filename = "test-llms-full.txt"',
        'llms_txt_filename = "custom-name.txt"',
    )

    with open(custom_conf, "w") as f:
        f.write(conf_content)

    # Create a new test app with the custom configuration
    app = SphinxTestApp(
        srcdir=src_dir,
        builddir=temp_dir,
        buildername="html",
        freshenv=True,
        confoverrides={"llms_txt_filename": "custom-name.txt"},
    )

    app.build()

    # Check if the output file with the custom name was created
    output_file = Path(app.outdir) / "custom-name.txt"
    assert output_file.exists(), f"Output file {output_file} does not exist"

    # Custom cleanup to avoid missing_ok issue
    import sys

    from sphinx.testing.util import _clean_up_global_state

    sys.path[:] = app._saved_path
    _clean_up_global_state()

    # Safe unlink that works with older Python versions
    if hasattr(app, "docutils_conf_path") and app.docutils_conf_path.exists():
        app.docutils_conf_path.unlink()


def test_max_lines_limit(temp_dir, rootdir):
    """Test that the max lines limit works correctly."""
    from sphinx.testing.util import SphinxTestApp

    src_dir = rootdir / "basic"

    # Create a new test app with a small line limit
    app = SphinxTestApp(
        srcdir=src_dir,
        builddir=temp_dir,
        buildername="html",
        freshenv=True,
        confoverrides={
            "llms_txt_filename": "limited.txt",
            "llms_txt_max_lines": 10,  # Set a small limit to trigger the warning
            "llms_txt_verbose": True,
        },
    )

    app.build()

    # Check that the output file was NOT created (since it would exceed the limit)
    output_file = Path(app.outdir) / "limited.txt"
    assert not output_file.exists(), f"Output file {output_file} exists but should not when limit is exceeded"

    # Custom cleanup to avoid missing_ok issue
    sys.path[:] = app._saved_path
    _clean_up_global_state()

    # Safe unlink
    if hasattr(app, "docutils_conf_path") and app.docutils_conf_path.exists():
        app.docutils_conf_path.unlink()
