"""Test the sphinx_llms_txt extension."""

from sphinx_llms_txt import LLMSFullManager, setup


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


def test_llms_full_manager_initialization():
    """Test initialization of LLMSFullManager."""
    manager = LLMSFullManager()
    assert manager.page_titles == {}
    assert manager.config == {}
    assert manager.master_doc is None
    assert manager.env is None


def test_manager_page_title_update():
    """Test updating page titles."""
    manager = LLMSFullManager()
    manager.update_page_title("doc1", "Title 1")
    manager.update_page_title("doc2", "Title 2")

    assert manager.page_titles["doc1"] == "Title 1"
    assert manager.page_titles["doc2"] == "Title 2"


def test_set_config():
    """Test setting configuration."""
    manager = LLMSFullManager()
    config = {
        "llms_txt_filename": "custom.txt",
        "llms_txt_verbose": True,
        "llms_txt_max_lines": 1000,
    }
    manager.set_config(config)
    assert manager.config == config


def test_set_master_doc():
    """Test setting master doc."""
    manager = LLMSFullManager()
    manager.set_master_doc("index")
    assert manager.master_doc == "index"


def test_empty_page_order():
    """Test get_page_order returns empty list when env or master_doc not set."""
    manager = LLMSFullManager()
    assert manager.get_page_order() == []

    # Set only master_doc, but not env
    manager.set_master_doc("index")
    assert manager.get_page_order() == []


def test_process_includes(tmp_path):
    """Test that include directives are processed correctly."""
    # Create a manager
    manager = LLMSFullManager()

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
    processed_content = manager._process_includes(source_content, source_file)

    # Check that the include directive was replaced with the content
    expected_content = "Line before include.\nThis is included content.\nWith multiple lines.\nLine after include."
    assert processed_content == expected_content


def test_process_includes_with_relative_paths(tmp_path):
    """Test that include directives with relative paths are processed correctly."""
    # Create a manager
    manager = LLMSFullManager()

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

    # Set the srcdir on the manager
    manager.srcdir = str(source_dir)

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
    processed_content = manager._process_includes(source_content, sources_file)

    # Check that the include directive was replaced with the content
    expected_content = "Line before include.\nThis is included content from another directory.\nLine after include."
    assert processed_content == expected_content
