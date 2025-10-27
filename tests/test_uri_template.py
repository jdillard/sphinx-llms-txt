"""Test URI template functionality for llms.txt links."""

from sphinx_llms_txt import FileWriter


def test_uri_template_with_sources_dir(tmp_path):
    """Test that default template uses _sources links when sources_dir exists."""
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Create _sources directory to simulate its existence
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Mock app with html_sourcelink_suffix
    class MockApp:
        class Config:
            html_sourcelink_suffix = ".txt"

        config = Config()

    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": (
            "{base_url}_sources/{docname}{suffix}{sourcelink_suffix}"
        ),
        "html_baseurl": "https://example.com",
    }
    writer = FileWriter(config, str(build_dir), MockApp())

    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Page order with suffixes (simulating _sources files exist)
    page_order = [("index", ".rst"), ("about", ".md")]

    writer.write_verbose_info_to_file(page_order, page_titles, 0, sources_dir)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should link to _sources files
    assert "- [Home Page](https://example.com/_sources/index.rst.txt)" in content
    assert "- [About Us](https://example.com/_sources/about.md.txt)" in content


def test_uri_template_without_sources_dir(tmp_path):
    """
    Test that HTML template is used when sources_dir doesn't exist and no custom
    template.
    """
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        # No custom template set
        "html_baseurl": "https://example.com",
    }
    writer = FileWriter(config, str(build_dir))

    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Page order without suffixes (simulating no _sources)
    page_order = [("index", None), ("about", None)]

    # Pass None for sources_dir to simulate it doesn't exist
    writer.write_verbose_info_to_file(page_order, page_titles, 0, None)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should fallback to HTML links
    assert "- [Home Page](https://example.com/index.html)" in content
    assert "- [About Us](https://example.com/about.html)" in content


def test_uri_template_custom_without_sources_dir(tmp_path):
    """
    Test that custom URI template is respected even when sources_dir doesn't exist.
    """
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": "{base_url}raw/{docname}{suffix}",
        "html_baseurl": "https://example.com/",
    }
    writer = FileWriter(config, str(build_dir))

    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Page order without suffixes (simulating no _sources)
    page_order = [("index", None), ("about", None)]

    # Pass None for sources_dir to simulate it doesn't exist
    writer.write_verbose_info_to_file(page_order, page_titles, 0, None)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should use custom template even without sources_dir
    assert "- [Home Page](https://example.com/raw/index)" in content
    assert "- [About Us](https://example.com/raw/about)" in content


def test_uri_template_custom(tmp_path):
    """Test that custom URI template works correctly."""
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Mock app with html_sourcelink_suffix
    class MockApp:
        class Config:
            html_sourcelink_suffix = ".txt"

        config = Config()

    # Custom template that uses different path
    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": "{base_url}raw/{docname}{suffix}",
        "html_baseurl": "https://example.com/",
    }
    writer = FileWriter(config, str(build_dir), MockApp())

    page_titles = {
        "index": "Home Page",
    }

    page_order = [("index", ".rst")]

    writer.write_verbose_info_to_file(page_order, page_titles, 0, sources_dir)

    verbose_file = build_dir / "llms.txt"
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should use custom template
    assert "- [Home Page](https://example.com/raw/index.rst)" in content


def test_uri_template_invalid_fallback(tmp_path):
    """
    Test that invalid template falls back to default sources template when
    sources_dir exists.
    """
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Mock app with html_sourcelink_suffix
    class MockApp:
        class Config:
            html_sourcelink_suffix = ".txt"

        config = Config()

    # Invalid template with typo in variable name
    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": "{base_urll}/{docname}",
        "html_baseurl": "https://example.com",
    }
    writer = FileWriter(config, str(build_dir), MockApp())

    page_titles = {
        "index": "Home Page",
    }

    page_order = [("index", ".rst")]

    writer.write_verbose_info_to_file(page_order, page_titles, 0, sources_dir)

    verbose_file = build_dir / "llms.txt"
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should fallback to default sources template
    assert "- [Home Page](https://example.com/_sources/index.rst.txt)" in content


def test_uri_template_invalid_fallback_no_sources(tmp_path):
    """
    Test that invalid template falls back to HTML template when sources_dir doesn't
    exist.
    """
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Invalid template with typo in variable name
    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": "{base_urll}/{docname}",
        "html_baseurl": "https://example.com",
    }
    writer = FileWriter(config, str(build_dir))

    page_titles = {
        "index": "Home Page",
    }

    page_order = [("index", None)]

    # Pass None for sources_dir
    writer.write_verbose_info_to_file(page_order, page_titles, 0, None)

    verbose_file = build_dir / "llms.txt"
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Should fallback to HTML template
    assert "- [Home Page](https://example.com/index.html)" in content


def test_uri_template_none_suffix_handling(tmp_path):
    """Test that None suffix values are handled as empty strings."""
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Mock app with html_sourcelink_suffix
    class MockApp:
        class Config:
            html_sourcelink_suffix = ".txt"

        config = Config()

    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": (
            "{base_url}_sources/{docname}{suffix}{sourcelink_suffix}"
        ),
        "html_baseurl": "https://example.com/",
    }
    writer = FileWriter(config, str(build_dir), MockApp())

    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Mix of pages with and without suffixes
    page_order = [("index", ".rst"), ("about", None)]

    writer.write_verbose_info_to_file(page_order, page_titles, 0, sources_dir)

    verbose_file = build_dir / "llms.txt"
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # First page should work normally
    assert "- [Home Page](https://example.com/_sources/index.rst.txt)" in content
    # Second page with None suffix should use empty string
    assert "- [About Us](https://example.com/_sources/about.txt)" in content


def test_uri_template_empty_sourcelink_suffix(tmp_path):
    """Test handling of empty html_sourcelink_suffix."""
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Mock app with empty html_sourcelink_suffix
    class MockApp:
        class Config:
            html_sourcelink_suffix = ""

        config = Config()

    config = {
        "llms_txt_file": True,
        "llms_txt_filename": "llms.txt",
        "llms_txt_uri_template": (
            "{base_url}_sources/{docname}{suffix}{sourcelink_suffix}"
        ),
        "html_baseurl": "https://example.com/",
    }
    writer = FileWriter(config, str(build_dir), MockApp())

    page_titles = {
        "index": "Home Page",
    }

    page_order = [("index", ".rst")]

    writer.write_verbose_info_to_file(page_order, page_titles, 0, sources_dir)

    verbose_file = build_dir / "llms.txt"
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # With empty sourcelink_suffix, should just use the source suffix
    assert "- [Home Page](https://example.com/_sources/index.rst)" in content
