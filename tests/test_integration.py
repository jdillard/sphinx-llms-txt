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

    # Check that the include directive has been processed
    assert "Page With Include" in content
    assert "This is a test page that includes another file:" in content
    assert "Changelog" in content  # Content from the included file
    assert "0.2.0 (2025-01-01)" in content  # Content from the included file
    assert "0.1.0 (2024-01-01)" in content  # Additional content from the included file
    assert "This content comes after the include." in content


def test_custom_filename(temp_dir, rootdir):
    """Test using a custom filename for the output."""
    from sphinx.testing.util import SphinxTestApp

    src_dir = rootdir / "basic"
    print(src_dir)

    # Create a copy of the configuration with a different filename
    custom_conf = src_dir / "conf_custom.py"
    with open(src_dir / "conf.py") as f:
        conf_content = f.read()

    conf_content = conf_content.replace(
        'llms_txt_full_filename = "test-llms-full.txt"',
        'llms_txt_full_filename = "custom-name.txt"',
    )

    with open(custom_conf, "w") as f:
        f.write(conf_content)

    # Create a new test app with the custom configuration
    app = SphinxTestApp(
        srcdir=src_dir,
        builddir=temp_dir,
        buildername="html",
        freshenv=True,
        confoverrides={"llms_txt_full_filename": "custom-name.txt"},
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
            "llms_txt_full_filename": "limited.txt",
            "llms_txt_full_max_size": 10,  # Set a small limit to trigger the warning
        },
    )

    app.build()

    # Check that the output file was NOT created (since it would exceed the limit)
    output_file = Path(app.outdir) / "limited.txt"
    assert (
        not output_file.exists()
    ), f"Output file {output_file} exists but should not when limit is exceeded"

    # Custom cleanup to avoid missing_ok issue
    sys.path[:] = app._saved_path
    _clean_up_global_state()

    # Safe unlink
    if hasattr(app, "docutils_conf_path") and app.docutils_conf_path.exists():
        app.docutils_conf_path.unlink()


def test_title_override(temp_dir, rootdir):
    """Test that the title override works correctly."""
    from sphinx.testing.util import SphinxTestApp

    src_dir = rootdir / "basic"

    # Custom title to override the default project name
    custom_title = "Custom Title Override"

    # Create a new test app with the title override
    app = SphinxTestApp(
        srcdir=src_dir,
        builddir=temp_dir,
        buildername="html",
        freshenv=True,
        confoverrides={
            "llms_txt_title": custom_title,
        },
    )

    app.build()

    # Check if the summary file was created
    summary_file = Path(app.outdir) / "llms.txt"
    assert summary_file.exists(), f"Summary file {summary_file} does not exist"

    # Read the content of the summary file
    content = summary_file.read_text()

    # Check that the custom title was used
    assert (
        f"# {custom_title}" in content
    ), f"Custom title '{custom_title}' not found in summary file"
    # Ensure the default project name was NOT used
    assert (
        "# Test Project" not in content
    ), "Default project name was used instead of custom title"

    # Custom cleanup to avoid missing_ok issue
    sys.path[:] = app._saved_path
    _clean_up_global_state()

    # Safe unlink
    if hasattr(app, "docutils_conf_path") and app.docutils_conf_path.exists():
        app.docutils_conf_path.unlink()


def test_exclusion(temp_dir, rootdir):
    """Test that the exclude patterns work correctly."""
    from sphinx.testing.util import SphinxTestApp

    src_dir = rootdir / "basic"

    # Create a new test app with exclude patterns
    app = SphinxTestApp(
        srcdir=src_dir,
        builddir=temp_dir,
        buildername="html",
        freshenv=True,
        confoverrides={
            "llms_txt_full_filename": "excluded.txt",
            "llms_txt_exclude": [
                "page1",
                "page_with_*",
            ],  # Exclude page1 and any page starting with page_with_
        },
    )

    app.build()

    # Check if the output file was created
    output_file = Path(app.outdir) / "excluded.txt"
    assert output_file.exists(), f"Output file {output_file} does not exist"

    # Read the content of the output file
    content = output_file.read_text()

    # Check that index and page2 content is included
    assert (
        "Welcome to Test Project's documentation!" in content
    )  # Index should be included
    assert "Page 2 Title" in content  # page2 title should be included
    assert "Content for section A" in content  # Content from page2 should be included

    # Check that excluded content is NOT included
    assert "Page 1 Title" not in content  # page1 title should be excluded
    assert (
        "Content for section 1" not in content
    )  # Content from page1 should be excluded
    assert (
        "Page With Include" not in content
    )  # page_with_include title should be excluded

    # Extra debug info for test
    print(f"\nContent snippet: {content[:500]}...\n")

    # Check that none of the content from page1 appears
    page1_phrases = [
        "Page 1 Title",
        "This is the content of page 1",
        "Section 1",
        "Content for section 1",
        "Section 2",
        "Content for section 2",
    ]
    for phrase in page1_phrases:
        assert phrase not in content, f"Found excluded content: '{phrase}'"

    # Custom cleanup to avoid missing_ok issue
    sys.path[:] = app._saved_path
    _clean_up_global_state()

    # Safe unlink
    if hasattr(app, "docutils_conf_path") and app.docutils_conf_path.exists():
        app.docutils_conf_path.unlink()
