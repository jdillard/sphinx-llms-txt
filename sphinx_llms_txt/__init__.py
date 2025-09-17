"""
Sphinx extension that generates llms.txt and llms-full.txt files for LLM consumption.

This extension collects documentation content from Sphinx projects and generates
two output files:
- llms.txt: A concise Markdown summary with project overview and page links
- llms-full.txt: A comprehensive reStructuredText file containing all documentation
  content with resolved includes and path references

The extension processes content during the build phase, handles page-level and
block-level ignore directives, and can optionally include source code files.
"""

from typing import Any, Dict

from docutils import nodes
from sphinx.application import Sphinx

from .collector import DocumentCollector
from .manager import LLMSFullManager
from .processor import DocumentProcessor
from .writer import FileWriter

__version__ = "0.5.3"

# Export classes needed by tests
__all__ = [
    "DocumentCollector",
    "DocumentProcessor",
    "FileWriter",
    "LLMSFullManager",
]

# Global manager instance
_manager = LLMSFullManager()

# Store root document first paragraph
_root_first_paragraph = ""


def doctree_resolved(app: Sphinx, doctree, docname: str):
    """Called when a docname has been resolved to a document."""
    global _root_first_paragraph

    # Check for llms-txt-ignore metadata at the page level
    if hasattr(app.env, "metadata") and docname in app.env.metadata:
        metadata = app.env.metadata[docname]
        if metadata.get("llms-txt-ignore", "").lower() in ("true", "1", "yes"):
            _manager.mark_page_ignored(docname)
            return

    # Extract title from the document
    title = None
    # findall() returns a generator, convert to list to check if it has elements
    title_nodes = list(doctree.findall(nodes.title))
    if title_nodes:
        title = title_nodes[0].astext()

    if title:
        _manager.update_page_title(docname, title)

    # Extract first paragraph from root document
    if docname == app.config.master_doc:
        for node in doctree.traverse(nodes.paragraph):
            first_para = node.astext()
            if first_para:
                _root_first_paragraph = first_para
                break


def build_finished(app: Sphinx, exception):
    """Called when the build is finished."""
    if exception is None:
        # Set the environment and master doc in the manager
        _manager.set_env(app.env)
        _manager.set_master_doc(app.config.master_doc)
        _manager.set_app(app)

        # Get the summary - use configured value or extracted first paragraph
        summary = app.config.llms_txt_summary
        if summary is None:
            summary = _root_first_paragraph

        # Set up configuration
        config = {
            "llms_txt_file": app.config.llms_txt_file,
            "llms_txt_filename": app.config.llms_txt_filename,
            "llms_txt_title": app.config.llms_txt_title,
            "llms_txt_summary": summary,
            "llms_txt_full_file": app.config.llms_txt_full_file,
            "llms_txt_full_filename": app.config.llms_txt_full_filename,
            "llms_txt_full_max_size": app.config.llms_txt_full_max_size,
            "llms_txt_full_size_policy": app.config.llms_txt_full_size_policy,
            "llms_txt_directives": app.config.llms_txt_directives,
            "llms_txt_exclude": app.config.llms_txt_exclude,
            "llms_txt_code_files": app.config.llms_txt_code_files,
            "llms_txt_code_base_path": app.config.llms_txt_code_base_path,
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

    app.add_config_value("llms_txt_file", True, "env")
    app.add_config_value("llms_txt_filename", "llms.txt", "env")
    app.add_config_value("llms_txt_full_file", True, "env")
    app.add_config_value("llms_txt_full_filename", "llms-full.txt", "env")
    app.add_config_value("llms_txt_full_max_size", None, "env")
    app.add_config_value("llms_txt_full_size_policy", "warn_skip", "env")
    app.add_config_value("llms_txt_directives", [], "env")
    app.add_config_value("llms_txt_title", None, "env")
    app.add_config_value("llms_txt_summary", None, "env")
    app.add_config_value("llms_txt_exclude", [], "env")
    app.add_config_value("llms_txt_code_files", [], "env")
    app.add_config_value("llms_txt_code_base_path", None, "env")

    def builder_inited(app):
        """Used to limit what builders are allowed to run the extension."""

        allowed_builders = ["html", "dirhtml"]
        if hasattr(app, "builder") and app.builder.name in allowed_builders:
            # Reset manager and root paragraph for each build
            global _manager, _root_first_paragraph
            _manager = LLMSFullManager()
            _root_first_paragraph = ""

            app.connect("doctree-resolved", doctree_resolved)
            app.connect("build-finished", build_finished)

    app.connect("builder-inited", builder_inited)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
