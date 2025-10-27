"""
File writer module for sphinx-llms-txt.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


class FileWriter:
    """Handles writing processed content to output files."""

    def __init__(self, config: Dict[str, Any], outdir: str = None, app: Sphinx = None):
        self.config = config
        self.outdir = outdir
        self.app = app

    def _resolve_uri_template(self, sources_dir: Path = None) -> str:
        """Resolve which URI template to use based on configuration and sources_dir.

        Args:
            sources_dir: Path to _sources directory (None if not found)

        Returns:
            The template string to use for generating URIs
        """
        # Step 1: Check if _sources directory exists globally
        if not sources_dir:
            # No _sources: Use HTML template for all pages
            return "{base_url}{docname}.html"

        # Step 2: Try user's configured template
        user_template = self.config.get(
            "llms_txt_uri_template",
            "{base_url}_sources/{docname}{suffix}{sourcelink_suffix}",
        )

        # Validate user's template by checking for valid variable names
        # Valid variables: base_url, docname, suffix, sourcelink_suffix
        try:
            # Try formatting with test values to validate syntax
            test_values = {
                "base_url": "http://example.com/",
                "docname": "test",
                "suffix": ".rst",
                "sourcelink_suffix": ".txt",
            }
            user_template.format(**test_values)
            # Template is valid, use it
            return user_template
        except (KeyError, ValueError) as e:
            # Template has invalid variables or syntax
            logger.warning(
                f"sphinx-llms-txt: Invalid llms_txt_uri_template: {e}. "
                f"Falling back to default."
            )
            # If _sources exists, use default sources template
            # (we already checked sources_dir exists above)
            return "{base_url}_sources/{docname}{suffix}{sourcelink_suffix}"

    def write_combined_file(
        self, content_parts: List[str], output_path: Path, total_line_count: int
    ) -> bool:
        """Write the combined content to a file.

        Args:
            content_parts: List of content strings to combine
            output_path: Path to write the output file
            total_line_count: Total number of lines in the content

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content_parts))

            logger.info(
                f"sphinx-llms-txt: Created {output_path} with {len(content_parts)}"
                f" sources and {total_line_count} lines"
            )
            return True
        except Exception as e:
            logger.error(f"sphinx-llms-txt: Error writing combined sources file: {e}")
            return False

    def write_verbose_info_to_file(
        self,
        page_order: Union[List[str], List[Tuple[str, str]]],
        page_titles: Dict[str, str],
        total_line_count: int = 0,
        sources_dir: Path = None,
    ) -> bool:
        """Write summary information to the llms.txt file.

        Args:
            page_order: Ordered list of document names or (docname, suffix) tuples
            page_titles: Dictionary mapping docnames to titles
            total_line_count: Total number of lines in the combined content
            sources_dir: Path to _sources directory (None if not found)

        Returns:
            True if successful, False otherwise
        """
        if not self.outdir:
            logger.warning(
                "sphinx-llms-txt: Cannot write verbose info to file: outdir not set"
            )
            return False

        output_path = Path(self.outdir) / self.config.get("llms_txt_filename")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                project_name = "llms-txt Summary"
                # First priority: use title from config if available
                if self.config.get("llms_txt_title"):
                    project_name = self.config.get("llms_txt_title")
                # Second priority: use project name from Sphinx app if available
                elif (
                    self.app
                    and hasattr(self.app, "config")
                    and hasattr(self.app.config, "project")
                ):
                    project_name = self.app.config.project
                f.write(f"# {project_name}\n\n")

                # Add description if available
                description = self.config.get("llms_txt_summary", "")
                if description:
                    # Trim leading and trailing whitespace
                    description = description.strip()
                    if description:
                        # Only add blockquote if description is not empty
                        # Replace newlines with newline + blockquote marker to maintain
                        # blockquote formatting
                        description = description.replace("\n", "\n> ")
                        f.write(f"> {description}\n\n")

                f.write("## Docs\n\n")
                # Get base URL from config
                base_url = self.config.get("html_baseurl", "/")
                # Ensure base_url ends with a trailing slash
                if not base_url.endswith("/"):
                    base_url += "/"

                # Get sourcelink suffix from Sphinx config
                sourcelink_suffix = ""
                if self.app and hasattr(self.app.config, "html_sourcelink_suffix"):
                    sourcelink_suffix = self.app.config.html_sourcelink_suffix
                    # Handle empty string case specially
                    if sourcelink_suffix == "":
                        sourcelink_suffix = ""  # Keep it empty
                    elif not sourcelink_suffix.startswith("."):
                        sourcelink_suffix = "." + sourcelink_suffix

                # Resolve which template to use
                uri_template = self._resolve_uri_template(sources_dir)

                for item in page_order:
                    # Handle both old format (str) and new format (tuple)
                    if isinstance(item, tuple):
                        docname, suffix = item
                    else:
                        docname = item
                        suffix = None

                    title = page_titles.get(docname, docname)

                    # Format the URI using the resolved template
                    # Step 3: Apply the chosen template (no per-page checks)
                    try:
                        uri = uri_template.format(
                            base_url=base_url,
                            docname=docname,
                            suffix=suffix or "",
                            sourcelink_suffix=sourcelink_suffix,
                        )
                    except (KeyError, ValueError) as e:
                        # Should not happen after validation, but fallback just in case
                        logger.warning(
                            f"sphinx-llms-txt: Error formatting URI for "
                            f"{docname}: {e}. Using HTML fallback."
                        )
                        uri = f"{base_url}{docname}.html"

                    f.write(f"- [{title}]({uri})\n")

            logger.info(f"sphinx-llms-txt: created {output_path}")
            return True
        except Exception as e:
            logger.error(f"sphinx-llms-txt: Error writing verbose info to file: {e}")
            return False
