"""
Sphinx extension to create a combined sources file (llms-full.txt)
"""

from typing import Any, Dict

from docutils import nodes
from sphinx.application import Sphinx

from .collector import DocumentCollector
from .manager import LLMSFullManager
from .processor import DocumentProcessor
from .writer import FileWriter

__version__ = "0.2.2"

# Export classes needed by tests
__all__ = [
    "DocumentCollector",
    "DocumentProcessor",
    "FileWriter",
    "LLMSFullManager",
]

# Global manager instance
_manager = LLMSFullManager()


def doctree_resolved(app: Sphinx, doctree, docname: str):
    """Called when a docname has been resolved to a document."""
    # Extract title from the document
    title = None
    # findall() returns a generator, convert to list to check if it has elements
    title_nodes = list(doctree.findall(nodes.title))
    if title_nodes:
        title = title_nodes[0].astext()

    if title:
        _manager.update_page_title(docname, title)


def build_finished(app: Sphinx, exception):
    """Called when the build is finished."""
    if exception is None:
        # Set the environment and master doc in the manager
        _manager.set_env(app.env)
        _manager.set_master_doc(app.config.master_doc)
        _manager.set_app(app)

        # Set up configuration
        config = {
            "llms_txt_file": app.config.llms_txt_file,
            "llms_txt_filename": app.config.llms_txt_filename,
            "llms_txt_title": app.config.llms_txt_title,
            "llms_txt_summary": app.config.llms_txt_summary,
            "llms_txt_full_file": app.config.llms_txt_full_file,
            "llms_txt_full_filename": app.config.llms_txt_full_filename,
            "llms_txt_full_max_size": app.config.llms_txt_full_max_size,
            "llms_txt_directives": app.config.llms_txt_directives,
            "llms_txt_exclude": app.config.llms_txt_exclude,
            "html_baseurl": getattr(app.config, "html_baseurl", ""),
        }
        _manager.set_config(config)

        # Get final titles from the environment at build completion
        if hasattr(app.env, "titles"):
            for docname, title_node in app.env.titles.items():
                if title_node:
                    title = title_node.astext()
                    _manager.update_page_title(docname, title)

        # Create the combined file
        _manager.combine_sources(app.outdir, app.srcdir)


def setup(app: Sphinx) -> Dict[str, Any]:
    """Set up the Sphinx extension."""

    # Add configuration options
    app.add_config_value("llms_txt_file", True, "env")
    app.add_config_value("llms_txt_filename", "llms.txt", "env")
    app.add_config_value("llms_txt_full_file", True, "env")
    app.add_config_value("llms_txt_full_filename", "llms-full.txt", "env")
    app.add_config_value("llms_txt_full_max_size", None, "env")
    app.add_config_value("llms_txt_directives", [], "env")
    app.add_config_value("llms_txt_title", None, "env")
    app.add_config_value("llms_txt_summary", None, "env")
    app.add_config_value("llms_txt_exclude", [], "env")

    # Connect to Sphinx events
    app.connect("doctree-resolved", doctree_resolved)
    app.connect("build-finished", build_finished)

    # Reset manager for each build
    global _manager
    _manager = LLMSFullManager()

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
