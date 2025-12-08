#!/usr/bin/env python3
"""
Generate variant llms.txt files for demo purposes.

Takes the generated llms.txt (with _sources links) and creates:
- llms.txt - default with _sources links (unchanged)
- llms.md.txt - .html.md links
- llms.rst.txt - .rst links
"""

import re
import sys
from pathlib import Path


def get_base_url() -> str:
    """Import base_url from conf.py."""
    sys.path.insert(0, str(Path(__file__).parent / "source"))
    from conf import html_baseurl  # noqa: E402

    return html_baseurl


def generate_variants(build_dir: Path) -> None:
    """Generate llms.txt variants from the original file."""
    original = build_dir / "llms.txt"

    if not original.exists():
        print(f"Error: {original} not found")
        sys.exit(1)

    content = original.read_text()
    base_url = get_base_url()

    # Pattern to match links like: https://.../_sources/{docname}.rst.txt
    link_pattern = re.compile(
        rf"({re.escape(base_url)})_sources/([a-zA-Z0-9_/\-]+)\.rst\.txt"
    )

    # Generate .html.md variant
    md_content = link_pattern.sub(r"\1\2.html.md", content)
    (build_dir / "llms.md.txt").write_text(md_content)
    print(f"Generated: {build_dir / 'llms.md.txt'} (.html.md links)")

    # Generate .rst variant
    rst_content = link_pattern.sub(r"\1\2.rst", content)
    (build_dir / "llms.rst.txt").write_text(rst_content)
    print(f"Generated: {build_dir / 'llms.rst.txt'} (.rst links)")

    print(f"Kept: {build_dir / 'llms.txt'} (_sources links)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        build_dir = Path(sys.argv[1])
    else:
        build_dir = Path("build/html")

    generate_variants(build_dir)
