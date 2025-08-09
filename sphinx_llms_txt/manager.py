"""
Main manager module for sphinx-llms-txt.
"""

import glob
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from .collector import DocumentCollector
from .processor import DocumentProcessor
from .writer import FileWriter

logger = logging.getLogger(__name__)


def _get_git_root(path: Path) -> Optional[Path]:
    """Get the git root directory for a given path."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _get_language_from_extension(file_path: Path) -> str:
    """Map file extension to language identifier for code blocks."""
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".fish": "fish",
        ".ps1": "powershell",
        ".html": "html",
        ".htm": "html",
        ".xml": "xml",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".conf": "ini",
        ".sql": "sql",
        ".md": "markdown",
        ".rst": "rst",
        ".txt": "text",
        ".dockerfile": "dockerfile",
        ".dockerignore": "text",
        ".gitignore": "text",
        ".gitattributes": "text",
        ".editorconfig": "ini",
        ".makefile": "makefile",
        ".r": "r",
        ".R": "r",
        ".m": "matlab",
        ".pl": "perl",
        ".lua": "lua",
        ".vim": "vim",
        ".vimrc": "vim",
        ".proto": "protobuf",
        ".thrift": "thrift",
        ".graphql": "graphql",
        ".gql": "graphql",
    }

    # Get the extension from the file path
    ext = file_path.suffix.lower()

    # Handle special cases like Makefile, Dockerfile without extension
    if not ext:
        name = file_path.name.lower()
        if name in ["makefile", "gnumakefile"]:
            return "makefile"
        elif name in ["dockerfile", "dockerfile.dev", "dockerfile.prod"]:
            return "dockerfile"
        elif name.startswith("dockerfile."):
            return "dockerfile"
        else:
            return "text"

    return extension_map.get(ext, "text")


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
        self.ignored_pages: set = set()

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

    def mark_page_ignored(self, docname: str):
        """Mark a page as ignored due to llms-txt-ignore metadata."""
        self.ignored_pages.add(docname)

    def _filter_ignored_pages(
        self, page_order: Union[List[str], List[Tuple[str, str]]]
    ) -> Union[List[str], List[Tuple[str, str]]]:
        """Filter out ignored pages from page_order."""
        filtered_pages = []
        for item in page_order:
            # Handle both old format (str) and new format (tuple)
            if isinstance(item, tuple):
                docname, _ = item
            else:
                docname = item

            if docname not in self.ignored_pages:
                filtered_pages.append(item)

        return filtered_pages

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
                # Avoid duplicate extensions when source_suffix == source_link_suffix
                if src_suffix == source_link_suffix:
                    source_file = sources_dir / f"{docname}{src_suffix}"
                    expected_suffix = src_suffix
                else:
                    source_file = (
                        sources_dir / f"{docname}{src_suffix}{source_link_suffix}"
                    )
                    expected_suffix = f"{src_suffix}{source_link_suffix}"

                if source_file.exists():
                    docname_to_file[docname] = source_file
                else:
                    logger.warning(
                        f"sphinx-llms-txt: Source file not found for: {docname}."
                        f"Expected: {docname}{expected_suffix}"
                    )
            else:
                logger.warning(
                    f"sphinx-llms-txt: No source suffix determined for: {docname}"
                )

        # Generate content
        content_parts = []

        # Track code files for later processing
        code_file_parts = []

        # Count lines in code files (initially 0)
        code_files_line_count = 0

        # Add pages in order
        added_files = set()
        total_line_count = code_files_line_count
        max_lines = self.config.get("llms_txt_full_max_size")

        # Parse size_policy configuration early to determine collection strategy
        size_policy_action = None
        aborted_due_to_size = False
        if max_lines is not None:
            size_policy = self.config.get("llms_txt_full_size_policy", "warn_skip")
            _, size_policy_action = self._parse_size_policy_config(size_policy)

        # Only collect all files if action is "keep"
        # For "skip" and "note", we can abort early when size limit is exceeded
        should_abort_early = size_policy_action in ["skip", "note"]

        for docname, _ in page_order:
            # Skip pages marked as ignored
            if docname in self.ignored_pages:
                logger.debug(f"sphinx-llms-txt: Skipping ignored page: {docname}")
                continue

            if docname in docname_to_file:
                file_path = docname_to_file[docname]
                content, line_count = self._read_source_file(file_path, docname)

                # Abort early for skip/note actions
                if (
                    max_lines is not None
                    and total_line_count + line_count > max_lines
                    and should_abort_early
                ):
                    logger.debug(
                        f"sphinx-llms-txt: Stopping collection due to size limit. "
                        f"File {docname} would exceed limit."
                    )
                    aborted_due_to_size = True
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
        # Only skip this if we aborted early due to size limits for skip/note actions
        size_limit_exceeded = max_lines is not None and total_line_count > max_lines
        if not (size_limit_exceeded and should_abort_early):
            # Get all source files in the _sources directory using configured suffixes
            source_suffixes = self._get_source_suffixes()
            all_source_files = []
            for src_suffix in source_suffixes:
                # Avoid duplicate extensions when source_suffix == source_link_suffix
                if src_suffix == source_link_suffix:
                    glob_pattern = f"**/*{src_suffix}"
                else:
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
                    # Avoid duplicate extensions when suffixes match
                    if src_suffix == source_link_suffix:
                        combined_suffix = src_suffix
                    else:
                        combined_suffix = f"{src_suffix}{source_link_suffix}"

                    if rel_path.endswith(combined_suffix):
                        docname = rel_path[: -len(combined_suffix)]  # Remove suffix
                        break

                if docname is None:
                    continue

                # Skip pages marked as ignored
                if docname in self.ignored_pages:
                    logger.debug(
                        f"sphinx-llms-txt: Skipping ignored remaining file: {docname}"
                    )
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

                # Abort early for skip/note actions
                if (
                    max_lines is not None
                    and total_line_count + line_count > max_lines
                    and should_abort_early
                ):
                    aborted_due_to_size = True
                    break

                if content:
                    logger.debug(f"sphinx-llms-txt: Adding remaining file: {docname}")
                    content_parts.append(content)
                    total_line_count += line_count

        # Process code files at the end if configured
        # Only skip this if we aborted early due to size limits for skip/note actions
        if not (size_limit_exceeded and should_abort_early):
            code_file_parts, processed_file_paths = self._process_code_files()
            code_files_line_count = sum(
                part.count("\n") + 1 for part in code_file_parts
            )

            # Check if adding code files would exceed the maximum line count
            # For "keep" action, we include code files regardless of size
            if (
                max_lines is not None
                and total_line_count + code_files_line_count > max_lines
                and should_abort_early
            ):
                logger.warning(
                    f"sphinx-llms-txt: Adding code files would exceed max line limit "
                    f"({max_lines}). Current: {total_line_count}, "
                    f"Code files: {code_files_line_count}. Skipping code files."
                )
                aborted_due_to_size = True
            else:
                # Add source code files section if there are any code files
                if code_file_parts:
                    section_header = self._create_code_files_section_header(
                        processed_file_paths
                    )
                    content_parts.append(section_header)
                    content_parts.extend(code_file_parts)
                    # Add line count for the section header too
                    total_line_count += (
                        code_files_line_count + section_header.count("\n") + 1
                    )
        else:
            # If we aborted early for skip/note actions, set empty code file parts
            code_file_parts = []

        # Handle size limit exceeded cases
        if max_lines is not None and (
            total_line_count > max_lines or aborted_due_to_size
        ):
            # Parse the size_policy configuration (reuse what we parsed earlier)
            size_policy = self.config.get("llms_txt_full_size_policy", "warn_skip")
            log_level, action = self._parse_size_policy_config(size_policy)

            # Log with the specified level
            filename = self.config.get("llms_txt_full_filename", "llms-full.txt")
            message = f"sphinx-llms-txt: Max lines ({max_lines}) exceeded for {filename}"  # noqa: E501

            if log_level == "info":
                logger.info(message)
            else:
                logger.warning(message)

            # Handle different actions
            if action == "skip":
                filename = self.config.get("llms_txt_full_filename", "llms-full.txt")
                logger.info(f"sphinx-llms-txt: Skipping {filename} generation")
                # Log summary information if requested
                if self.config.get("llms_txt_file"):
                    filtered_page_order = self._filter_ignored_pages(page_order)
                    self.writer.write_verbose_info_to_file(
                        filtered_page_order,
                        self.collector.page_titles,
                        total_line_count,
                    )
                return
            elif action == "note":
                logger.info(f"sphinx-llms-txt: Creating placeholder {output_path}")
                self._write_placeholder_file(output_path, max_lines)

                # Log summary information if requested
                if self.config.get("llms_txt_file"):
                    filtered_page_order = self._filter_ignored_pages(page_order)
                    self.writer.write_verbose_info_to_file(
                        filtered_page_order,
                        self.collector.page_titles,
                        total_line_count,
                    )
                return
            elif action == "keep":
                filename = self.config.get("llms_txt_full_filename", "llms-full.txt")
                # Fall through to write the file

        # Write combined file only if we have content to write
        if content_parts:
            success = self.writer.write_combined_file(
                content_parts, output_path, total_line_count
            )
        else:
            success = False

        # Log summary information if requested
        if success and self.config.get("llms_txt_file"):
            filtered_page_order = self._filter_ignored_pages(page_order)
            self.writer.write_verbose_info_to_file(
                filtered_page_order, self.collector.page_titles, total_line_count
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

    def _process_code_files(self) -> Tuple[List[str], List[Path]]:
        """Process code files specified in llms_txt_code_files configuration.

        Supports include/exclude patterns with +:/- : prefixes:
        - '+:pattern' = include files matching pattern
        - '-:pattern' = exclude files matching pattern
        - 'pattern' (no prefix) = ignored (no special handling)

        Returns:
            Tuple of (formatted code block strings, list of processed file paths)
        """
        code_file_patterns = self.config.get("llms_txt_code_files", [])
        if not code_file_patterns:
            return [], []

        # Parse patterns into include and exclude lists
        include_patterns = []
        exclude_patterns = []

        for pattern in code_file_patterns:
            if pattern.startswith("-:"):
                exclude_patterns.append(pattern[2:])  # Remove the '-:' prefix
            elif pattern.startswith("+:"):
                include_patterns.append(pattern[2:])  # Remove the '+:' prefix
            else:
                # No prefix = log warning about ignored pattern
                logger.warning(
                    f"sphinx-llms-txt: Code file pattern '{pattern}' ignored."
                    f"Use '+:{pattern}' to include or '-:{pattern}' to exclude."
                )

        # If no include patterns specified, nothing to process
        if not include_patterns:
            return [], []

        code_parts = []
        processed_files = set()
        all_matching_files = set()

        # First, collect all files matching include patterns
        for pattern in include_patterns:
            # Resolve pattern relative to source directory
            if self.srcdir:
                pattern_path = Path(self.srcdir) / pattern
            else:
                pattern_path = Path(pattern)

            # Use glob to find matching files
            matching_files = glob.glob(str(pattern_path), recursive=True)

            for file_path_str in matching_files:
                file_path = Path(file_path_str)
                if file_path.is_file():  # Only add files, not directories
                    all_matching_files.add(file_path.resolve())

        # Filter out files matching exclude patterns
        filtered_files = set()
        for file_path in all_matching_files:
            should_exclude = False

            for exclude_pattern in exclude_patterns:
                # Resolve exclude pattern relative to source directory
                if self.srcdir:
                    exclude_pattern_path = Path(self.srcdir) / exclude_pattern
                else:
                    exclude_pattern_path = Path(exclude_pattern)

                # Check if this file matches the exclude pattern
                exclude_matches = glob.glob(str(exclude_pattern_path), recursive=True)
                if str(file_path) in exclude_matches:
                    should_exclude = True
                    logger.debug(
                        f"sphinx-llms-txt: Excluding code file: {file_path} "
                        f"(matched pattern: {exclude_pattern})"
                    )
                    break

            if not should_exclude:
                filtered_files.add(file_path)

        # Sort files for consistent ordering
        sorted_files = sorted(filtered_files)

        for file_path in sorted_files:
            # Skip if already processed (shouldn't happen with set, but safety check)
            if file_path in processed_files:
                continue

            try:
                # Read the file content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Get language identifier
                language = _get_language_from_extension(file_path)

                # Get relative path from source directory for title
                if self.srcdir:
                    try:
                        title = file_path.relative_to(Path(self.srcdir))

                        # Strip base path if configured,
                        # or auto-detect from git root
                        base_path = self.config.get("llms_txt_code_base_path")
                        if base_path is None:
                            # Auto-detect: try to make path relative to git root
                            git_root = _get_git_root(Path(self.srcdir))
                            if git_root:
                                try:
                                    # Get srcdir relative to git root
                                    srcdir_relative = Path(self.srcdir).relative_to(
                                        git_root
                                    )
                                    # Calculate relative path from srcdir to
                                    # git root
                                    if srcdir_relative != Path("."):
                                        # Count directory levels to go up
                                        up_levels = len(srcdir_relative.parts)
                                        base_path = "../" * up_levels
                                    else:
                                        base_path = None
                                except ValueError:
                                    base_path = None

                        if base_path:
                            title_str = str(title)
                            if title_str.startswith(base_path):
                                title = Path(title_str[len(base_path) :])
                    except ValueError:
                        # File is not relative to srcdir, use filename
                        title = file_path.name
                else:
                    title = file_path.name

                # Format as code block with equals underline
                title_str = str(title)
                equals_line = "=" * len(title_str)

                # Indent the content for reStructuredText code-block directive
                indented_content = "\n".join(
                    f"   {line}" if line.strip() else ""
                    for line in content.splitlines()
                )

                code_block = f"""
{title_str}
{equals_line}

.. code-block:: {language}

{indented_content}"""
                code_parts.append(code_block)

                processed_files.add(file_path)
                logger.debug(f"sphinx-llms-txt: Added code file: {title}")

            except Exception as e:
                logger.warning(
                    f"sphinx-llms-txt: Error reading code file {file_path}: {e}"
                )
                continue

        return code_parts, sorted(processed_files)

    def _create_code_files_section_header(self, file_paths: List[Path] = None) -> str:
        """Create the section header for source code files.

        Args:
            file_paths: List of file paths that were added to generate tree view

        Returns:
            String containing the section header with title, underlines, description,
            and file tree
        """
        section_title = "Source Code Files"
        star_line = "*" * len(section_title)

        description = "This section contains source code files from the project repository. These files are included to provide implementation context and technical details that complement the documentation above."  # noqa: E501

        header = f"""
{star_line}
{section_title}
{star_line}

{description}"""

        # Add file tree if file paths are provided
        if file_paths:
            tree_display = self._generate_file_tree(file_paths)
            header += f"""

**Files included:**

.. code-block:: text

{tree_display}"""

        return header

    def _generate_file_tree(self, file_paths: List[Path]) -> str:
        """Generate a tree-like representation of file paths.

        Args:
            file_paths: List of file paths to display in tree format

        Returns:
            String containing indented tree representation of the files
        """
        if not file_paths:
            return ""

        # Convert to relative paths if possible and create tree structure
        tree_data = {}

        for file_path in sorted(file_paths):
            # Get relative path from source directory for display
            if self.srcdir:
                try:
                    rel_path = file_path.relative_to(Path(self.srcdir))

                    # Apply base path stripping logic similar to code processing
                    base_path = self.config.get("llms_txt_code_base_path")
                    if base_path is None:
                        # Auto-detect: try to make path relative to git root
                        git_root = _get_git_root(Path(self.srcdir))
                        if git_root:
                            try:
                                # Get srcdir relative to git root
                                srcdir_relative = Path(self.srcdir).relative_to(
                                    git_root
                                )
                                # Calculate relative path from srcdir to git root
                                if srcdir_relative != Path("."):
                                    # Count directory levels to go up
                                    up_levels = len(srcdir_relative.parts)
                                    base_path = "../" * up_levels
                                else:
                                    base_path = None
                            except ValueError:
                                base_path = None

                    if base_path:
                        rel_path_str = str(rel_path)
                        if rel_path_str.startswith(base_path):
                            rel_path = Path(rel_path_str[len(base_path) :])

                except ValueError:
                    # File is not relative to srcdir, use filename
                    rel_path = Path(file_path.name)
            else:
                rel_path = Path(file_path.name)

            # Build nested dictionary structure
            parts = rel_path.parts
            current = tree_data
            for part in parts[:-1]:  # All but the last part (directories)
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add the file (last part)
            if parts:
                current[parts[-1]] = None  # None indicates it's a file

        # Convert tree structure to string representation
        lines = []
        self._format_tree_node(tree_data, lines, "", True)

        # Indent each line for reStructuredText code block
        indented_lines = [f"   {line}" for line in lines]
        return "\n".join(indented_lines)

    def _format_tree_node(
        self, node: dict, lines: List[str], prefix: str, is_root: bool
    ):
        """Recursively format tree nodes into lines with proper tree characters.

        Args:
            node: Dictionary representing the tree structure
            lines: List to append formatted lines to
            prefix: Current prefix for indentation and tree characters
            is_root: Whether this is the root level (no tree characters)
        """
        if not node:
            return

        items = sorted(node.items())

        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1

            if is_root:
                # Root level - no tree characters
                current_prefix = ""
                next_prefix = ""
            else:
                # Use tree characters
                current_prefix = prefix + ("└── " if is_last else "├── ")
                next_prefix = prefix + ("    " if is_last else "│   ")

            lines.append(current_prefix + name)

            # Recursively handle subdirectories
            if subtree is not None:  # It's a directory
                self._format_tree_node(subtree, lines, next_prefix, False)

    def _parse_size_policy_config(self, size_policy: str) -> tuple[str, str]:
        """Parse the llms_txt_full_size_policy configuration value.

        Args:
            size_policy: Configuration string in format "loglevel_action"

        Returns:
            Tuple of (log_level, action) where:
            - log_level is "warn" or "info"
            - action is "keep", "skip", or "note"
        """
        if not size_policy or "_" not in size_policy:
            logger.warning(
                f"sphinx-llms-txt: Invalid llms_txt_full_size_policy "
                f"format: '{size_policy}'. "
                f"Using default 'warn_skip'."
            )
            return "warn", "skip"

        parts = size_policy.split("_", 1)  # Split on first underscore only
        log_level, action = parts[0], parts[1]

        # Validate log level
        if log_level not in ["warn", "info"]:
            logger.warning(
                f"sphinx-llms-txt: Invalid log level '{log_level}' in "
                f"llms_txt_full_size_policy. "
                f"Valid options: warn, info. Using 'warn'."
            )
            log_level = "warn"

        # Validate action
        if action not in ["keep", "skip", "note"]:
            logger.warning(
                f"sphinx-llms-txt: Invalid action '{action}' in "
                f"llms_txt_full_size_policy. "
                f"Valid options: keep, skip, note. Using 'skip'."
            )
            action = "skip"

        return log_level, action

    def _write_placeholder_file(self, output_path: Path, max_lines: int):
        """Write a placeholder llms-full.txt file with a note about size limit.

        Args:
            output_path: Path where the placeholder file should be written
            max_lines: The configured maximum line limit
        """
        # Create the placeholder note content
        placeholder_content = (
            f".. This file was not generated because it exceeded the configured size limit.\n"  # noqa: E501
            "   See the conf.py ``llms_txt_full_max_size`` and ``llms_txt_full_size_policy``\n"  # noqa: E501
            "   for configuration options.\n"
            "\n"
            f"   Configured max size: {max_lines} lines\n"
            "\n"
            "   For more information, see: https://sphinx-llms-txt.readthedocs.io/en/latest/configuration-values.html#llms-txt-full-max-size\n"  # noqa: E501
        )

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(placeholder_content)
            logger.debug(f"sphinx-llms-txt: Wrote placeholder file: {output_path}")
        except Exception as e:
            logger.error(
                f"sphinx-llms-txt: Error writing placeholder file {output_path}: {e}"
            )
