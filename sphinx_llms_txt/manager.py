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

        # Get the correct page order
        page_order = self.collector.get_page_order()

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
        for f in sources_dir.glob("**/*.txt"):
            logger.debug(f"sphinx-llms-txt: Found source file: {f.stem} at {f}")
            txt_files[f.stem] = f

        # Log discovered files and page order
        logger.debug(f"sphinx-llms-txt: Found {len(txt_files)} source files")
        logger.debug(f"sphinx-llms-txt: Page order (after exclusion): {page_order}")

        # Log exclusion patterns
        exclude_patterns = self.config.get("llms_txt_exclude")
        if exclude_patterns:
            logger.debug(f"sphinx-llms-txt: Exclusion patterns: {exclude_patterns}")

        # Create a mapping from docnames to actual file names
        docname_to_file = {}

        # Try exact matches first
        for docname in page_order:
            # Skip excluded pages
            if any(
                self.collector._match_exclude_pattern(docname, pattern)
                for pattern in exclude_patterns
            ):
                continue

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
        total_line_count = 0
        max_lines = self.config.get("llms_txt_full_max_size")
        abort_due_to_max_lines = False

        for docname in page_order:
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
                logger.warning(f"sphinx-llm-txt: Source file not found for: {docname}")

        # Add any remaining files (in alphabetical order) if not aborted
        if not abort_due_to_max_lines:
            # Apply the same exclusion filter to remaining files
            exclude_patterns = self.config.get("llms_txt_exclude")

            # Create a set of files to exclude based on their basename
            excluded_files = set()
            for pattern in exclude_patterns:
                if "*" not in pattern and "?" not in pattern:
                    # For exact patterns, add variants
                    excluded_files.add(pattern)
                    excluded_files.add(f"{pattern}.rst")
                    excluded_files.add(f"{pattern}.txt")
                    excluded_files.add(pattern.replace("-", "_"))
                    excluded_files.add(pattern.replace("_", "-"))

            # Filter remaining files
            remaining_files = sorted(
                [
                    name
                    for name in txt_files
                    if name not in added_files
                    and name not in excluded_files
                    and not any(
                        self.collector._match_exclude_pattern(name, pattern)
                        for pattern in exclude_patterns
                    )
                ]
            )
            if remaining_files:
                logger.info(f"Adding remaining files: {remaining_files}")
            for file_stem in remaining_files:
                file_path = txt_files[file_stem]
                content, line_count = self._read_source_file(file_path, file_stem)

                # Check if adding this file would exceed the maximum line count
                if max_lines is not None and total_line_count + line_count > max_lines:
                    break

                # Double-check that this file should be included
                should_include = True
                file_stem = file_path.stem
                exclude_patterns = self.config.get("llms_txt_exclude")

                if exclude_patterns:
                    # Check stem against exclusion patterns
                    if any(
                        self.collector._match_exclude_pattern(file_stem, pattern)
                        for pattern in exclude_patterns
                    ):
                        logger.debug(
                            "sphinx-llms-txt: Final exclusion check removed remaining"
                            f" file: {file_stem}"
                        )
                        should_include = False

                if content and should_include:
                    content_parts.append(content)
                    total_line_count += line_count

        # Check if line limit was exceeded before creating the file
        max_lines = self.config.get("llms_txt_full_max_size")
        if abort_due_to_max_lines or (
            max_lines is not None and total_line_count > max_lines
        ):
            logger.warning(
                f"sphinx-llm-txt: Max line limit ({max_lines}) exceeded:"
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
            logger.error(f"sphinx-llm-txt: Error reading source file {file_path}: {e}")
            return "", 0
