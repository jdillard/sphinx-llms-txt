"""
Sphinx extension to create a combined sources file (llms-full.txt)
"""

from pathlib import Path
from typing import Any, Dict, List

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

__version__ = "0.1.0"

logger = logging.getLogger(__name__)


class LLMSFullManager:
    """Manages the collection and ordering of documentation sources."""

    def __init__(self):
        self.page_titles: Dict[str, str] = {}
        self.config: Dict[str, Any] = {}
        self.master_doc: str = None
        self.env: BuildEnvironment = None

    def set_master_doc(self, master_doc: str):
        """Set the master document name."""
        self.master_doc = master_doc

    def set_env(self, env: BuildEnvironment):
        """Set the Sphinx environment."""
        self.env = env

    def update_page_title(self, docname: str, title: str):
        """Update the title for a page."""
        if title:
            self.page_titles[docname] = title

    def set_config(self, config: Dict[str, Any]):
        """Set configuration options."""
        self.config = config

    def get_page_order(self) -> List[str]:
        """Get the correct page order from the toctree structure."""
        if not self.env or not self.master_doc:
            return []

        page_order = []
        visited = set()

        def collect_from_toctree(docname: str):
            """Recursively collect documents from toctree."""
            if docname in visited:
                return

            visited.add(docname)

            # Add the current document
            if docname not in page_order:
                page_order.append(docname)

            # Check for toctree entries in this document
            try:
                # Look for toctree_includes which contains the direct children
                if (
                    hasattr(self.env, "toctree_includes")
                    and docname in self.env.toctree_includes
                ):
                    for child_docname in self.env.toctree_includes[docname]:
                        collect_from_toctree(child_docname)
                else:
                    # Fallback: try to resolve and parse the toctree
                    toctree = self.env.get_and_resolve_toctree(docname, None)
                    if toctree:
                        from docutils import nodes

                        # Use findall() instead of traverse() to avoid deprecation warning
                        # Convert generator to list for iteration
                        for node in list(toctree.findall(nodes.reference)):
                            if "refuri" in node.attributes:
                                refuri = node.attributes["refuri"]
                                if refuri and refuri.endswith(".html"):
                                    child_docname = refuri[:-5]  # Remove .html
                                    if (
                                        child_docname != docname
                                    ):  # Avoid circular references
                                        collect_from_toctree(child_docname)
            except Exception as e:
                logger.debug(f"Could not get toctree for {docname}: {e}")

        # Start from the master document
        collect_from_toctree(self.master_doc)

        # Add any remaining documents not in the toctree (sorted)
        if hasattr(self.env, "all_docs"):
            remaining = sorted(
                [doc for doc in self.env.all_docs.keys() if doc not in page_order]
            )
            page_order.extend(remaining)

        return page_order

    def combine_sources(self, outdir: str, srcdir: str):
        """Combine all source files into a single file."""
        # Get the correct page order
        page_order = self.get_page_order()

        if not page_order:
            logger.warning(
                "Could not determine page order, skipping llms-full creation"
            )
            return

        # Determine output file name and location
        output_filename = self.config.get("llms_txt_filename")
        output_path = Path(outdir) / output_filename

        # Find sources directory
        sources_dir = None
        possible_sources = [
            Path(outdir) / "_sources",
            Path(outdir) / "html" / "_sources",
            Path(outdir) / "singlehtml" / "_sources",
        ]

        for path in possible_sources:
            if path.exists():
                sources_dir = path
                break

        if not sources_dir:
            logger.warning(
                "Could not find _sources directory, skipping llms-full creation"
            )
            return

        # Collect all available source files
        txt_files = {}
        for f in sources_dir.glob("*.txt"):
            txt_files[f.stem] = f

        # Create a mapping from docnames to actual file names
        docname_to_file = {}

        # Try exact matches first
        for docname in page_order:
            if docname in txt_files:
                docname_to_file[docname] = txt_files[docname]
            else:
                # Try with .rst extension
                if f"{docname}.rst" in txt_files:
                    docname_to_file[docname] = txt_files[f"{docname}.rst"]
                # Try with .txt extension
                elif f"{docname}.txt" in txt_files:
                    docname_to_file[docname] = txt_files[f"{docname}.txt"]
                # Try with underscores instead of hyphens
                elif docname.replace("-", "_") in txt_files:
                    docname_to_file[docname] = txt_files[docname.replace("-", "_")]
                # Try with hyphens instead of underscores
                elif docname.replace("_", "-") in txt_files:
                    docname_to_file[docname] = txt_files[docname.replace("_", "-")]

        # Generate content
        content_parts = []

        # Add pages in order
        added_files = set()

        for docname in page_order:
            if docname in docname_to_file:
                file_path = docname_to_file[docname]
                content = self._read_source_file(file_path, docname)
                if content:
                    content_parts.append(content)
                    added_files.add(file_path.stem)
            else:
                logger.warning(f"Source file not found for: {docname}")

        # Add any remaining files (in alphabetical order)
        remaining_files = sorted(
            [name for name in txt_files if name not in added_files]
        )
        if remaining_files:
            logger.info(f"Adding remaining files: {remaining_files}")
        for file_stem in remaining_files:
            file_path = txt_files[file_stem]
            content = self._read_source_file(file_path, file_stem)
            if content:
                content_parts.append(content)

        # Write combined file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content_parts))

            logger.info(
                f"sphinx-llms-txt: created {output_path} with {len(txt_files)} sources"
            )

            # Log summary information if requested
            if self.config.get("llms_txt_verbose"):
                self._log_summary_info(page_order)

        except Exception as e:
            logger.error(f"Error writing combined sources file: {e}")

    def _read_source_file(self, file_path: Path, docname: str) -> str:
        """Read and format a single source file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            section_lines = [content, ""]

            return "\n".join(section_lines)

        except Exception as e:
            logger.error(f"Error reading source file {file_path}: {e}")
            return ""

    def _log_summary_info(self, page_order: List[str]):
        """Log summary information to the logger."""
        logger.info("")
        logger.info("llms-txt Summary")
        logger.info("================")
        logger.info(f"Total pages: {len(page_order)}")
        logger.info(f"Configuration: {self.config}")
        logger.info("Page order:")
        for i, docname in enumerate(page_order, 1):
            title = self.page_titles.get(docname, docname)
            logger.info(f"{i:3d}. {docname} - {title}")


# Global manager instance
_manager = LLMSFullManager()


def doctree_resolved(app: Sphinx, doctree, docname: str):
    """Called when a docname has been resolved to a document."""
    # Extract title from the document
    from docutils import nodes

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

        # Set up configuration
        config = {
            "llms_txt_filename": app.config.llms_txt_filename,
            "llms_txt_verbose": app.config.llms_txt_verbose,
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
    app.add_config_value("llms_txt_filename", "llms-full.txt", "env")
    app.add_config_value("llms_txt_verbose", False, "env")

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
