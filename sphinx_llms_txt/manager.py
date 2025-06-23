"""
Main manager module for sphinx-llms-txt.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from .collector import DocumentCollector
from .processor import DocumentProcessor
from .writer import FileWriter

logger = logging.getLogger(__name__)


class LLMSFullManager:
    """Manages the collection and ordering of documentation sources."""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.collector = DocumentCollector()
        self.processor = None
        self.writer = None
        self.master_doc: str = None
        self.env: BuildEnvironment = None
        self.srcdir: Optional[str] = None
        self.outdir: Optional[str] = None
        self.app: Optional[Sphinx] = None

    def set_master_doc(self, master_doc: str):
        """Set the master document name."""
        self.master_doc = master_doc
        self.collector.set_master_doc(master_doc)

    def set_env(self, env: BuildEnvironment):
        """Set the Sphinx environment."""
        self.env = env
        self.collector.set_env(env)

    def update_page_title(self, docname: str, title: str):
        """Update the title for a page."""
        self.collector.update_page_title(docname, title)

    def set_config(self, config: Dict[str, Any]):
        """Set configuration options."""
        self.config = config
        self.collector.set_config(config)

        # Initialize processor and writer with config
        self.processor = DocumentProcessor(config, self.srcdir)
        self.writer = FileWriter(config, self.outdir, self.app)

    def set_app(self, app: Sphinx):
        """Set the Sphinx application reference."""
        self.app = app
        self.collector.set_app(app)
        if self.writer:
            self.writer.app = app

    def combine_sources(self, outdir: str, srcdir: str):
        """Combine all source files into a single file."""
        # Store the source directory for resolving include directives
        self.srcdir = srcdir
        self.outdir = outdir

        # Update processor and writer with directories
        self.processor = DocumentProcessor(self.config, srcdir)
        self.writer = FileWriter(self.config, outdir, self.app)

        # Find sources directory first so we can pass it to get_page_order
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

        # Get the correct page order with source suffixes
        page_order = self.collector.get_page_order(sources_dir)

        if not page_order:
            logger.warning(
                "Could not determine page order, skipping llms-full creation"
            )
            return

        # Apply exclusion filter if configured
        page_order = self.collector.filter_excluded_pages(page_order)

        # Determine output file name and location
        output_filename = self.config.get("llms_txt_full_filename")
        output_path = Path(outdir) / output_filename

        # Log discovered files and page order
        logger.debug(f"sphinx-llms-txt: Page order (after exclusion): {page_order}")

        # Log exclusion patterns
        exclude_patterns = self.config.get("llms_txt_exclude")
        if exclude_patterns:
            logger.debug(f"sphinx-llms-txt: Exclusion patterns: {exclude_patterns}")

        # Create a mapping from docnames to source files
        docname_to_file = {}

        # Get the source link suffix from Sphinx config
        source_link_suffix = (
            self.app.config.html_sourcelink_suffix if self.app else ".txt"
        )

        # Handle empty string case specially
        if source_link_suffix == "":
            source_link_suffix = ""  # Keep it empty
        elif not source_link_suffix.startswith("."):
            source_link_suffix = "." + source_link_suffix

        # Process each (docname, suffix) in the page order
        for docname, src_suffix in page_order:
            # Skip excluded pages
            if exclude_patterns and any(
                self.collector._match_exclude_pattern(docname, pattern)
                for pattern in exclude_patterns
            ):
                continue

            # Build the source file path directly using the known suffix
            if src_suffix:
                source_file = sources_dir / f"{docname}{src_suffix}{source_link_suffix}"
                if source_file.exists():
                    docname_to_file[docname] = source_file
                else:
                    logger.warning(
                        f"sphinx-llms-txt: Source file not found for: {docname}."
                        f"Expected: {docname}{src_suffix}{source_link_suffix}"
                    )
            else:
                logger.warning(
                    f"sphinx-llms-txt: No source suffix determined for: {docname}"
                )

        # Generate content
        content_parts = []

        # Add pages in order
        added_files = set()
        total_line_count = 0
        max_lines = self.config.get("llms_txt_full_max_size")
        abort_due_to_max_lines = False

        for docname, _ in page_order:
            if docname in docname_to_file:
                file_path = docname_to_file[docname]
                content, line_count = self._read_source_file(file_path, docname)

                # Check if adding this file would exceed the maximum line count
                if max_lines is not None and total_line_count + line_count > max_lines:
                    abort_due_to_max_lines = True
                    break

                # Double-check this file should be included (not in excluded patterns)
                exclude_patterns = self.config.get("llms_txt_exclude")
                file_stem = file_path.stem
                should_include = True

                if exclude_patterns:
                    # Check stem and docname against exclusion patterns
                    if any(
                        self.collector._match_exclude_pattern(file_stem, pattern)
                        for pattern in exclude_patterns
                    ) or any(
                        self.collector._match_exclude_pattern(docname, pattern)
                        for pattern in exclude_patterns
                    ):
                        logger.debug(
                            f"sphinx-llms-txt: Final exclusion check removed: {docname}"
                        )
                        should_include = False

                if content and should_include:
                    content_parts.append(content)
                    added_files.add(file_path.stem)
                    total_line_count += line_count
            else:
                logger.warning(
                    f"sphinx-llms-txt: Source file not found for: {docname}. Check that"
                    f" file exists at _sources/{docname}[suffix]{source_link_suffix}"
                )

        # Add any remaining files (in alphabetical order) that aren't in the page order
        if not abort_due_to_max_lines:
            # Get all source files in the _sources directory using configured suffixes
            source_suffixes = self._get_source_suffixes()
            all_source_files = []
            for src_suffix in source_suffixes:
                glob_pattern = f"**/*{src_suffix}{source_link_suffix}"
                all_source_files.extend(sources_dir.glob(glob_pattern))

            processed_paths = set(file.resolve() for file in docname_to_file.values())

            # Find files that haven't been processed yet
            remaining_source_files = [
                f for f in all_source_files if f.resolve() not in processed_paths
            ]

            # Sort the remaining files for consistent ordering
            remaining_source_files.sort()

            if remaining_source_files:
                logger.info(
                    f"Found {len(remaining_source_files)} additional files not in"
                    f" toctree"
                )

            for file_path in remaining_source_files:
                # Extract docname from path by removing the source and link suffixes
                rel_path = str(file_path.relative_to(sources_dir))
                docname = None

                # Try each source suffix to find which one this file uses
                for src_suffix in source_suffixes:
                    combined_suffix = f"{src_suffix}{source_link_suffix}"
                    if rel_path.endswith(combined_suffix):
                        docname = rel_path[: -len(combined_suffix)]  # Remove suffix
                        break

                if docname is None:
                    continue

                # Skip excluded docnames
                if exclude_patterns and any(
                    self.collector._match_exclude_pattern(docname, pattern)
                    for pattern in exclude_patterns
                ):
                    logger.debug(f"sphinx-llms-txt: Skipping excluded file: {docname}")
                    continue

                # Read and process the file
                content, line_count = self._read_source_file(file_path, docname)

                # Check if adding this file would exceed the maximum line count
                if max_lines is not None and total_line_count + line_count > max_lines:
                    break

                if content:
                    logger.debug(f"sphinx-llms-txt: Adding remaining file: {docname}")
                    content_parts.append(content)
                    total_line_count += line_count

        # Check if line limit was exceeded before creating the file
        max_lines = self.config.get("llms_txt_full_max_size")
        if abort_due_to_max_lines or (
            max_lines is not None and total_line_count > max_lines
        ):
            logger.warning(
                f"sphinx-llms-txt: Max line limit ({max_lines}) exceeded:"
                f" {total_line_count} > {max_lines}. "
                f"Not creating llms-full.txt file."
            )

            # Log summary information if requested
            if self.config.get("llms_txt_file"):
                self.writer.write_verbose_info_to_file(
                    page_order, self.collector.page_titles, total_line_count
                )

            return

        # Write combined file if limit wasn't exceeded
        success = self.writer.write_combined_file(
            content_parts, output_path, total_line_count
        )

        # Log summary information if requested
        if success and self.config.get("llms_txt_file"):
            self.writer.write_verbose_info_to_file(
                page_order, self.collector.page_titles, total_line_count
            )

    def _read_source_file(self, file_path: Path, docname: str) -> Tuple[str, int]:
        """Read and format a single source file.

        Handles include directives by replacing them with the content of the included
        file, and processes directives with paths that need to be resolved.

        Returns:
            tuple: (content_str, line_count) where line_count is the number of lines
                   in the file
        """
        # Check if this file should be excluded by looking at the doc name
        exclude_patterns = self.config.get("llms_txt_exclude")
        if exclude_patterns and any(
            self.collector._match_exclude_pattern(docname, pattern)
            for pattern in exclude_patterns
        ):
            return "", 0

        try:
            # Check if the file stem (without extension) should be excluded
            file_stem = file_path.stem
            if exclude_patterns and any(
                self.collector._match_exclude_pattern(file_stem, pattern)
                for pattern in exclude_patterns
            ):
                return "", 0

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Process include directives and directives with paths
            content = self.processor.process_content(content, file_path)

            # Count the lines in the content
            line_count = content.count("\n") + (0 if content.endswith("\n") else 1)

            section_lines = [content, ""]
            content_str = "\n".join(section_lines)

            # Add 2 for the section_lines (content + empty line)
            return content_str, line_count + 1

        except Exception as e:
            logger.error(f"sphinx-llms-txt: Error reading source file {file_path}: {e}")
            return "", 0

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
