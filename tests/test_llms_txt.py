"""Test the sphinx_llms_txt extension."""

from sphinx_llms_txt import (
    DocumentCollector,
    DocumentProcessor,
    FileWriter,
    LLMSFullManager,
    setup,
)


def test_version():
    """Test that the version is defined."""
    from sphinx_llms_txt import __version__

    assert __version__


def test_setup_returns_valid_dict():
    """Test that the setup function returns a valid dict."""

    # Mock a Sphinx app
    class MockApp:
        def __init__(self):
            self.config_values = {}
            self.connections = {}

        def add_config_value(self, name, default, rebuild):
            self.config_values[name] = (default, rebuild)

        def connect(self, event, handler):
            self.connections[event] = handler

    app = MockApp()
    result = setup(app)

    # Check that result is a dict
    assert isinstance(result, dict)
    assert "version" in result
    assert "parallel_read_safe" in result
    assert "parallel_write_safe" in result


def test_document_collector_initialization():
    """Test initialization of DocumentCollector."""
    collector = DocumentCollector()
    assert collector.page_titles == {}
    assert collector.config == {}
    assert collector.master_doc is None
    assert collector.env is None


def test_document_processor_initialization():
    """Test initialization of DocumentProcessor."""
    config = {"llms_txt_directives": []}
    processor = DocumentProcessor(config)
    assert processor.config == config
    assert processor.srcdir is None


def test_file_writer_initialization():
    """Test initialization of FileWriter."""
    config = {"llms_txt_filename": "llms.txt"}
    writer = FileWriter(config)
    assert writer.config == config
    assert writer.outdir is None
    assert writer.app is None


def test_llms_full_manager_initialization():
    """Test initialization of LLMSFullManager."""
    manager = LLMSFullManager()
    assert manager.config == {}
    assert isinstance(manager.collector, DocumentCollector)
    assert manager.processor is None
    assert manager.writer is None
    assert manager.master_doc is None
    assert manager.env is None


def test_collector_page_title_update():
    """Test updating page titles."""
    collector = DocumentCollector()
    collector.update_page_title("doc1", "Title 1")
    collector.update_page_title("doc2", "Title 2")

    assert collector.page_titles["doc1"] == "Title 1"
    assert collector.page_titles["doc2"] == "Title 2"


def test_manager_page_title_update():
    """Test updating page titles through manager."""
    manager = LLMSFullManager()
    manager.update_page_title("doc1", "Title 1")
    manager.update_page_title("doc2", "Title 2")

    assert manager.collector.page_titles["doc1"] == "Title 1"
    assert manager.collector.page_titles["doc2"] == "Title 2"


def test_set_config():
    """Test setting configuration."""
    manager = LLMSFullManager()
    config = {
        "llms_txt_full_filename": "custom.txt",
        "llms_txt_file": True,
        "llms_txt_full_max_size": 1000,
    }
    manager.set_config(config)
    assert manager.config == config
    assert manager.collector.config == config
    assert isinstance(manager.processor, DocumentProcessor)
    assert isinstance(manager.writer, FileWriter)


def test_set_master_doc():
    """Test setting master doc."""
    manager = LLMSFullManager()
    manager.set_master_doc("index")
    assert manager.master_doc == "index"
    assert manager.collector.master_doc == "index"


def test_empty_page_order():
    """Test get_page_order returns empty list when env or master_doc not set."""
    collector = DocumentCollector()
    assert collector.get_page_order() == []

    # Set only master_doc, but not env
    collector.set_master_doc("index")
    assert collector.get_page_order() == []


def test_process_includes(tmp_path):
    """Test that include directives are processed correctly."""
    # Create a processor
    config = {"llms_txt_directives": []}
    processor = DocumentProcessor(config)

    # Create a test file with an include directive
    include_content = "This is included content.\nWith multiple lines."
    include_file = tmp_path / "included.txt"
    with open(include_file, "w", encoding="utf-8") as f:
        f.write(include_content)

    # Create a source file that includes the test file
    source_content = (
        "Line before include.\n.. include:: included.txt\nLine after include."
    )
    source_file = tmp_path / "source.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the include directive
    processed_content = processor._process_includes(source_content, source_file)

    # Check that the include directive was replaced with the content
    expected_content = (
        "Line before include.\nThis is included content.\nWith multiple"
        " lines.\nLine after include."
    )
    assert processed_content == expected_content


def test_process_includes_with_relative_paths(tmp_path):
    """Test that include directives with relative paths are processed correctly."""
    # Create a processor
    config = {"llms_txt_directives": []}

    # Set up a more complex directory structure
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create the original source directory structure
    source_dir = docs_dir / "source"
    source_dir.mkdir()

    # Create a subdirectory
    subdir = source_dir / "subdir"
    subdir.mkdir()

    # Create an includes directory
    includes_dir = source_dir / "includes"
    includes_dir.mkdir()

    # Create a processor with srcdir
    processor = DocumentProcessor(config, str(source_dir))

    # Create the included file in the includes directory
    include_content = "This is included content from another directory."
    include_file = includes_dir / "common.txt"
    with open(include_file, "w", encoding="utf-8") as f:
        f.write(include_content)

    # Create a source file in the subdirectory that includes the file from includes
    source_content = (
        "Line before include.\n.. include:: ../includes/common.txt\nLine after include."
    )
    source_file = subdir / "page.txt"
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Create the _sources directory to mimic Sphinx build output
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    sources_dir = build_dir / "_sources"
    sources_dir.mkdir()

    # Create the same structure in the _sources directory
    sources_subdir = sources_dir / "subdir"
    sources_subdir.mkdir()

    # Copy the source file to the _sources directory
    sources_file = sources_subdir / "page.txt"
    with open(sources_file, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Process the include directive from the _sources file
    processed_content = processor._process_includes(source_content, sources_file)

    # Check that the include directive was replaced with the content
    expected_content = (
        "Line before include.\nThis is included content from another"
        " directory.\nLine after include."
    )
    assert processed_content == expected_content


def test_match_exclude_pattern():
    """Test the _match_exclude_pattern method."""
    # Create a collector
    collector = DocumentCollector()

    # Test exact match
    assert collector._match_exclude_pattern("page1", "page1") is True
    assert collector._match_exclude_pattern("page1", "page2") is False

    # Test glob-style patterns
    assert collector._match_exclude_pattern("page1", "page*") is True
    assert collector._match_exclude_pattern("page_with_include", "page_with_*") is True
    assert collector._match_exclude_pattern("page1", "*1") is True
    assert collector._match_exclude_pattern("subdir/page1", "*/page1") is True
    assert collector._match_exclude_pattern("page1", "subdir/*") is False


def test_write_verbose_info_to_file(tmp_path):
    """Test writing verbose info to a file."""
    # Create a build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Create writer with configuration and outdir
    config = {
        "llms_txt_file": True,
        "llms_txt_full_max_size": 1000,
        "llms_txt_filename": "llms.txt",
    }
    writer = FileWriter(config, str(build_dir))

    # Create page titles
    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Create a page order
    page_order = ["index", "about"]

    # Call the method to write verbose info to file
    writer.write_verbose_info_to_file(page_order, page_titles)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that the content contains expected information
    assert "## Docs" in content
    # Without html_baseurl, URLs should start with /
    assert "- [Home Page](/index.html)" in content
    assert "- [About Us](/about.html)" in content


def test_write_verbose_info_with_baseurl(tmp_path):
    """Test writing verbose info to a file with html_baseurl set."""
    # Create a build directory
    build_dir = tmp_path / "build"
    build_dir.mkdir()

    # Create writer with configuration including html_baseurl
    config = {
        "llms_txt_file": True,
        "llms_txt_full_max_size": 1000,
        "llms_txt_filename": "llms.txt",
        "html_baseurl": "https://example.com",
    }
    writer = FileWriter(config, str(build_dir))

    # Create page titles
    page_titles = {
        "index": "Home Page",
        "about": "About Us",
    }

    # Create a page order
    page_order = ["index", "about"]

    # Call the method to write verbose info to file
    writer.write_verbose_info_to_file(page_order, page_titles)

    # Check that the file was created
    verbose_file = build_dir / "llms.txt"
    assert verbose_file.exists()

    # Read the file content
    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that the content contains expected information with baseurl
    assert "## Docs" in content
    assert "- [Home Page](https://example.com/index.html)" in content
    assert "- [About Us](https://example.com/about.html)" in content

    # Test with baseurl without trailing slash
    config["html_baseurl"] = "https://example.org"
    writer = FileWriter(config, str(build_dir))
    writer.write_verbose_info_to_file(page_order, page_titles)

    with open(verbose_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "- [Home Page](https://example.org/index.html)" in content
    assert "- [About Us](https://example.org/about.html)" in content
