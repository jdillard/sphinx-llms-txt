"""
Document collector module for sphinx-llms-txt.
"""

import fnmatch
from typing import Any, Dict, List, Tuple

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
        self.app = None

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

    def set_app(self, app):
        """Set the Sphinx application reference."""
        self.app = app

    def _get_source_suffixes(self):
        """Get all valid source file suffixes from Sphinx configuration.

        Returns:
            list: List of source file suffixes (e.g., ['.rst', '.md', '.txt'])
        """
        if not self.app:
            return [".rst"]  # Default fallback

        source_suffix = self.app.config.source_suffix

        if isinstance(source_suffix, dict):
            return list(source_suffix.keys())
        elif isinstance(source_suffix, list):
            return source_suffix
        else:
            return [source_suffix]  # String format

    def _get_docname_suffix(self, docname: str, sources_dir) -> str:
        """
        Determine the source suffix for a given docname by checking which
        file exists.

        Args:
            docname: The document name to check
            sources_dir: Path to the _sources directory

        Returns:
            The source suffix if found, or None if no matching file exists
        """
        if not sources_dir or not sources_dir.exists():
            return None

        # Get the source link suffix from Sphinx config
        source_link_suffix = ""
        if self.app and hasattr(self.app.config, "html_sourcelink_suffix"):
            source_link_suffix = self.app.config.html_sourcelink_suffix
            # Handle empty string case specially
            if source_link_suffix == "":
                source_link_suffix = ""  # Keep it empty
            elif not source_link_suffix.startswith("."):
                source_link_suffix = "." + source_link_suffix

        # Get the source file suffixes from Sphinx config
        source_suffixes = self._get_source_suffixes()

        # Try to find the source file with any of the valid source suffixes
        for src_suffix in source_suffixes:
            # Avoid duplicate extensions when source_suffix == source_link_suffix
            if src_suffix == source_link_suffix:
                candidate_file = sources_dir / f"{docname}{src_suffix}"
            else:
                candidate_file = (
                    sources_dir / f"{docname}{src_suffix}{source_link_suffix}"
                )
            if candidate_file.exists():
                return src_suffix

        return None

    def get_page_order(self, sources_dir=None) -> List[Tuple[str, str]]:
        """Get the correct page order from the toctree structure.

        Args:
            sources_dir: Optional path to _sources directory for suffix detection

        Returns:
            List of tuples (docname, source_suffix) in toctree order
        """
        if not self.env or not self.master_doc:
            return []

        page_order = []
        visited = set()

        def collect_from_toctree(docname: str):
            """Recursively collect documents from toctree."""
            if docname in visited:
                return

            visited.add(docname)

            # Add the current document with its suffix
            if docname not in [doc for doc, _ in page_order]:
                suffix = None
                if sources_dir:
                    suffix = self._get_docname_suffix(docname, sources_dir)
                page_order.append((docname, suffix))

            # Check for toctree entries in this document
            try:
                # Look for toctree_includes which contains the direct children
                if (
                    hasattr(self.env, "toctree_includes")
                    and docname in self.env.toctree_includes
                ):
                    for child_docname in self.env.toctree_includes[docname]:
                        collect_from_toctree(child_docname)
                # Try to use dependencies to find related documents
                elif (
                    hasattr(self.env, "dependencies")
                    and docname in self.env.dependencies
                ):
                    # Extract the dependent documents from the dependencies dict
                    for child_docname in self.env.dependencies[docname]:
                        # Only add documents actually in the document set
                        if (
                            hasattr(self.env, "all_docs")
                            and child_docname in self.env.all_docs
                        ):
                            collect_from_toctree(child_docname)
                # Fallback to titles or other available references
                elif hasattr(self.env, "titles") and hasattr(self.env, "all_docs"):
                    # Get all document names
                    all_docnames = list(self.env.all_docs.keys())

                    # Look for documents that might be related (have similar paths)
                    current_prefix = "/".join(docname.split("/")[:-1])
                    if current_prefix:
                        for child_docname in all_docnames:
                            # Documents in the same directory might be related
                            if (
                                child_docname.startswith(current_prefix)
                                and child_docname != docname
                            ):
                                collect_from_toctree(child_docname)
            except Exception as e:
                logger.debug(f"Could not get toctree for {docname}: {e}")

        # Start from the master document
        collect_from_toctree(self.master_doc)

        # Add any remaining documents not in the toctree (sorted)
        if hasattr(self.env, "all_docs"):
            processed_docnames = {doc for doc, _ in page_order}
            remaining = sorted(
                [
                    doc
                    for doc in self.env.all_docs.keys()
                    if doc not in processed_docnames
                ]
            )
            for docname in remaining:
                suffix = None
                if sources_dir:
                    suffix = self._get_docname_suffix(docname, sources_dir)
                page_order.append((docname, suffix))

        return page_order

    def filter_excluded_pages(
        self, page_order: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """Filter out excluded pages from the page order."""
        exclude_patterns = self.config.get("llms_txt_exclude")
        if exclude_patterns:
            return [
                (docname, suffix)
                for docname, suffix in page_order
                if not any(
                    self._match_exclude_pattern(docname, pattern)
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
