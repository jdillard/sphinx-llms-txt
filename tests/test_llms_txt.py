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
