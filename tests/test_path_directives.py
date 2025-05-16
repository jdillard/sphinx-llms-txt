"""Test the path directive processing functionality in sphinx_llms_txt."""

from sphinx_llms_txt import LLMSFullManager


def test_process_path_directives(tmp_path):
    """Test that path directives are processed correctly."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager with default directives
    manager.set_config(
        {
            "llms_txt_path_directives": [],
            "llms_txt_base_url": "",
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_path_directives(source_content, source_file)

    # With our implementation, the paths should have subdirectory paths added
    expected_content = (
        "Some content.\n"
        ".. image:: subdir/images/test.png\n"
        "More content.\n"
        ".. figure:: subdir/images/figure.png\n"
        "   :alt: A test figure\n"
    )

    assert processed_content == expected_content


def test_process_path_directives_with_base_url(tmp_path):
    """Test path directives with base_url configured using llms_txt_base_url."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager with default directives and base_url using llms_txt_base_url
    manager.set_config(
        {
            "llms_txt_path_directives": [],
            "llms_txt_base_url": "https://example.com/docs",
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_path_directives(source_content, source_file)

    # Expected: The paths should include the base URL with 'subdir' prefix
    expected_content = ".. image:: https://example.com/docs/subdir/images/test.png\n"

    assert processed_content == expected_content


def test_process_path_directives_with_html_baseurl(tmp_path):
    """Test path directives with base_url configured using html_baseurl."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager with default directives and base_url using html_baseurl (Sphinx built-in)
    manager.set_config(
        {
            "llms_txt_path_directives": [],
            "html_baseurl": "https://sphinx-docs.org/",
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_path_directives(source_content, source_file)

    # Expected: The paths should include the base URL with 'subdir' prefix
    expected_content = ".. image:: https://sphinx-docs.org/subdir/images/test.png\n"

    assert processed_content == expected_content


def test_process_path_directives_both_base_urls(tmp_path):
    """Test path directives with both html_baseurl and llms_txt_base_url configured."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager with both html_baseurl and llms_txt_base_url (html_baseurl should take precedence)
    manager.set_config(
        {
            "llms_txt_path_directives": [],
            "html_baseurl": "https://sphinx-docs.org/",
            "llms_txt_base_url": "https://example.com/docs",
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_path_directives(source_content, source_file)

    # Expected: The paths should include the html_baseurl (which takes precedence) with 'subdir' prefix
    expected_content = ".. image:: https://sphinx-docs.org/subdir/images/test.png\n"

    assert processed_content == expected_content


def test_process_path_directives_absolute_urls(tmp_path):
    """Test that absolute URLs are not modified."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager with default directives
    manager.set_config(
        {
            "llms_txt_path_directives": [],
            "llms_txt_base_url": "https://example.com/docs",
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_path_directives(source_content, source_file)

    assert processed_content == source_content


def test_process_path_directives_custom_directives(tmp_path):
    """Test that custom directives are processed correctly."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager with custom directives
    manager.set_config(
        {
            "llms_txt_path_directives": ["drawio-figure", "drawio-image"],
            "llms_txt_base_url": "",
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_path_directives(source_content, source_file)

    # Expected: The paths should be resolved to full paths
    expected_content = (
        ".. drawio-image:: diagrams/architecture.drawio\n"
        ".. drawio-figure:: diagrams/workflow.drawio\n"
        "   :alt: Workflow diagram\n"
    )

    assert processed_content == expected_content


def test_process_content_end_to_end(tmp_path):
    """Test the full _process_content method handling both includes and path directives."""
    # Create a manager
    manager = LLMSFullManager()

    # Configure the manager
    manager.set_config(
        {
            "llms_txt_path_directives": ["drawio-figure"],
            "html_baseurl": "https://sphinx-docs.org/",  # Using html_baseurl (Sphinx built-in)
        }
    )

    # Create source directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    manager.srcdir = str(src_dir)

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
    processed_content = manager._process_content(source_content, source_file)

    # Expected: Both includes and path directives should be processed
    expected_content = (
        "Some content.\n"
        "This is included content with an image:\n"
        # The included image isn't processed by path directives as it's part of the included content
        ".. image:: img/included.png\n"
        "More content.\n"
        # Images and custom directives in the main file are processed with html_baseurl
        ".. image:: https://sphinx-docs.org/subdir/images/test.png\n"
        ".. drawio-figure:: https://sphinx-docs.org/subdir/diagrams/arch.drawio\n"
    )

    assert processed_content == expected_content
