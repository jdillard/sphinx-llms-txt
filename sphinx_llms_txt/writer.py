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
    ) -> bool:
        """Write summary information to the llms.txt file.

        Args:
            page_order: Ordered list of document names or (docname, suffix) tuples
            page_titles: Dictionary mapping docnames to titles
            total_line_count: Total number of lines in the combined content

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

                for item in page_order:
                    # Handle both old format (str) and new format (tuple)
                    if isinstance(item, tuple):
                        docname, _ = item
                    else:
                        docname = item
                    title = page_titles.get(docname, docname)
                    f.write(f"- [{title}]({base_url}{docname}.html)\n")

            logger.info(f"sphinx-llms-txt: created {output_path}")
            return True
        except Exception as e:
            logger.error(f"sphinx-llms-txt: Error writing verbose info to file: {e}")
            return False
