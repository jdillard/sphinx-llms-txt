"""Test the path directive processing functionality in sphinx_llms_txt."""

from sphinx_llms_txt import DocumentProcessor


def test_process_path_directives(tmp_path):
    """Test that path directives are processed correctly."""
    # Create a processor
    config = {
        "llms_txt_directives": [],
        "html_baseurl": "",
    }
    processor = DocumentProcessor(config)

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    processor.srcdir = str(src_dir)

    # Create _sources directory to mimic Sphinx output
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Create a subdirectory in both places
    subdir = src_dir / "subdir"
    subdir.mkdir()
    sources_subdir = sources_dir / "subdir"
    sources_subdir.mkdir()

    # Create a source file with image directives
    source_content = (
        "Some content.\n"
        ".. image:: images/test.png\n"
        "More content.\n"
        ".. figure:: images/figure.png\n"
        "   :alt: A test figure\n"
    )

    # Create source file in sources directory to simulate Sphinx build output
    source_file = sources_subdir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the directives
    processed_content = processor._process_path_directives(source_content, source_file)

    # With our implementation, the paths should have subdirectory paths added
    expected_content = (
        "Some content.\n"
        ".. image:: subdir/images/test.png\n"
        "More content.\n"
        ".. figure:: subdir/images/figure.png\n"
        "   :alt: A test figure\n"
    )

    assert processed_content == expected_content


def test_process_path_directives_with_html_baseurl(tmp_path):
    """Test path directives with base_url configured using html_baseurl."""
    # Create a processor
    config = {
        "llms_txt_directives": [],
        "html_baseurl": "https://sphinx-docs.org/",
    }
    processor = DocumentProcessor(config)

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    processor.srcdir = str(src_dir)

    # Create _sources directory to mimic Sphinx output
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Create a subdirectory for file placement
    subdir = src_dir / "subdir"
    subdir.mkdir()
    sources_subdir = sources_dir / "subdir"
    sources_subdir.mkdir()

    # Create a source file with image directives
    source_content = ".. image:: images/test.png\n"

    # Create source file in sources directory to simulate Sphinx build output
    source_file = sources_subdir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the directives
    processed_content = processor._process_path_directives(source_content, source_file)

    # Expected: The paths should include the base URL with 'subdir' prefix
    expected_content = ".. image:: https://sphinx-docs.org/subdir/images/test.png\n"

    assert processed_content == expected_content


def test_process_path_directives_absolute_urls(tmp_path):
    """Test that absolute URLs are not modified."""
    # Create a processor
    config = {
        "llms_txt_directives": [],
        "html_baseurl": "https://example.com/docs",
    }
    processor = DocumentProcessor(config)

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    processor.srcdir = str(src_dir)

    # Create a source file with absolute URL image directives
    source_content = (
        ".. image:: https://othersite.com/images/test.png\n"
        ".. image:: /absolute/path/image.png\n"
        ".. image:: data:image/png;base64,iVBORw0KG...\n"
    )

    # Create source file
    source_file = src_dir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the directives (should remain unchanged)
    processed_content = processor._process_path_directives(source_content, source_file)

    assert processed_content == source_content


def test_process_path_directives_custom_directives(tmp_path):
    """Test that custom directives are processed correctly."""
    # Create a processor
    config = {
        "llms_txt_directives": ["drawio-figure", "drawio-image"],
        "html_baseurl": "",
    }
    processor = DocumentProcessor(config)

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    processor.srcdir = str(src_dir)

    # Create _sources directory to mimic Sphinx output
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Create a source file with custom directives
    source_content = (
        ".. drawio-image:: diagrams/architecture.drawio\n"
        ".. drawio-figure:: diagrams/workflow.drawio\n"
        "   :alt: Workflow diagram\n"
    )

    # Create source file in sources directory to simulate Sphinx build output
    source_file = sources_dir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the directives
    processed_content = processor._process_path_directives(source_content, source_file)

    # Expected: The paths should be resolved to full paths
    expected_content = (
        ".. drawio-image:: diagrams/architecture.drawio\n"
        ".. drawio-figure:: diagrams/workflow.drawio\n"
        "   :alt: Workflow diagram\n"
    )

    assert processed_content == expected_content


def test_process_content_end_to_end(tmp_path):
    """
    Test the full process_content method handling both includes and path directives.
    """
    # Create a processor
    config = {
        "llms_txt_directives": ["drawio-figure"],
        "html_baseurl": "https://sphinx-docs.org/",
    }
    processor = DocumentProcessor(config, str(tmp_path / "src"))

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    # Create an includes directory
    includes_dir = src_dir / "includes"
    includes_dir.mkdir()

    # Create a subdirectory for page placement
    subdir = src_dir / "subdir"
    subdir.mkdir()

    # Create an included file
    include_content = (
        "This is included content with an image:\n.. image:: img/included.png\n"
    )
    include_file = includes_dir / "fragment.txt"
    with open(include_file, "w", encoding="utf-8") as f:
        f.write(include_content)

    # Create a source file with both include and path directives
    source_content = (
        "Some content.\n"
        ".. include:: includes/fragment.txt\n"
        "More content.\n"
        ".. image:: images/test.png\n"
        ".. drawio-figure:: diagrams/arch.drawio\n"
    )

    # Create _sources directory to mimic Sphinx output
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Create _sources subdirectory
    sources_subdir = sources_dir / "subdir"
    sources_subdir.mkdir()

    # Create source file in sources directory to simulate Sphinx build output
    source_file = sources_subdir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the content
    processed_content = processor.process_content(source_content, source_file)

    # Expected: Both includes and path directives should be processed
    expected_content = (
        "Some content.\n"
        "This is included content with an image:\n"
        # The included image also gets processed by path directives as it's part of
        # the processed content
        ".. image:: https://sphinx-docs.org/subdir/img/included.png\n"
        "\n"  # There's an extra newline after the included content
        "More content.\n"
        # Images and custom directives in the main file are processed with html_baseurl
        ".. image:: https://sphinx-docs.org/subdir/images/test.png\n"
        ".. drawio-figure:: https://sphinx-docs.org/subdir/diagrams/arch.drawio\n"
    )

    assert processed_content == expected_content
