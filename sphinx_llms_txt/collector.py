"""
Document collector module for sphinx-llms-txt.
"""

import fnmatch
from typing import Any, Dict, List

from sphinx.environment import BuildEnvironment
from sphinx.util import logging

logger = logging.getLogger(__name__)


class DocumentCollector:
    """Collects and orders documentation sources based on toctree structure."""

    def __init__(self):
        self.page_titles: Dict[str, str] = {}
        self.master_doc: str = None
        self.env: BuildEnvironment = None
        self.config: Dict[str, Any] = {}

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

    def filter_excluded_pages(self, page_order: List[str]) -> List[str]:
        """Filter out excluded pages from the page order."""
        exclude_patterns = self.config.get("llms_txt_exclude")
        if exclude_patterns:
            return [
                page
                for page in page_order
                if not any(
                    self._match_exclude_pattern(page, pattern)
                    for pattern in exclude_patterns
                )
            ]
        return page_order

    def _match_exclude_pattern(self, docname: str, pattern: str) -> bool:
        """Check if a document name matches an exclude pattern.

        Args:
            docname: The document name to check
            pattern: The pattern to match against

        Returns:
            True if the document should be excluded, False otherwise
        """
        # Exact match
        if docname == pattern:
            return True

        # Glob-style pattern matching
        if fnmatch.fnmatch(docname, pattern):
            return True

        return False
