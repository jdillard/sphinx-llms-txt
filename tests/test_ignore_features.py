"""Tests for llms-txt ignore features."""

from pathlib import Path

from sphinx_llms_txt import DocumentProcessor


def test_process_ignore_blocks():
    """Test that ignore blocks are properly removed from content."""
    processor = DocumentProcessor({}, None)

    content = """This content should remain.

.. llms-txt-ignore-start

This content should be removed.

Section Ignored
---------------

This section should also be removed.

.. llms-txt-ignore-end

This content should remain after the ignore block.

.. llms-txt-ignore-start

Another ignored block.
Multiple lines here.

.. llms-txt-ignore-end

Final content that should remain."""

    processed = processor._process_ignore_blocks(content)

    # Check that ignored content is removed
    assert "This content should be removed." not in processed
    assert "Section Ignored" not in processed
    assert "Another ignored block." not in processed
    assert "Multiple lines here." not in processed

    # Check that non-ignored content remains
    assert "This content should remain." in processed
    assert "This content should remain after the ignore block." in processed
    assert "Final content that should remain." in processed


def test_process_ignore_blocks_with_indentation():
    """Test that ignore blocks work with different indentation levels."""
    processor = DocumentProcessor({}, None)

    content = """Section Title
=============

Normal content.

   .. llms-txt-ignore-start

   Indented ignored content.
   More indented content.

   .. llms-txt-ignore-end

Back to normal content."""

    processed = processor._process_ignore_blocks(content)

    # Check that ignored content is removed
    assert "Indented ignored content." not in processed
    assert "More indented content." not in processed

    # Check that non-ignored content remains
    assert "Section Title" in processed
    assert "Normal content." in processed
    assert "Back to normal content." in processed


def test_process_ignore_blocks_multiple():
    """Test that multiple ignore blocks are handled correctly."""
    processor = DocumentProcessor({}, None)

    content = """Start content.

.. llms-txt-ignore-start

First ignore block.

.. llms-txt-ignore-end

Middle content that should remain.

.. llms-txt-ignore-start

Second ignore block.

.. llms-txt-ignore-end

End content."""

    processed = processor._process_ignore_blocks(content)

    # Check that ignored content is removed
    assert "First ignore block." not in processed
    assert "Second ignore block." not in processed

    # Check that non-ignored content remains
    assert "Start content." in processed
    assert "Middle content that should remain." in processed
    assert "End content." in processed


def test_build_with_ignore_features(basic_sphinx_app):
    """Test building HTML documentation with ignore features."""
    app = basic_sphinx_app
    app.build()

    # Check if the output file was created
    output_file = Path(app.outdir) / "test-llms-full.txt"
    assert output_file.exists(), f"Output file {output_file} does not exist"

    # Read the content of the output file
    content = output_file.read_text()

    # Check that page with metadata ignore is completely excluded
    assert "Page Ignored by Metadata" not in content
    assert "This page should not appear in llms-full.txt" not in content

    # Check that page with ignore blocks has the right content
    assert "Page With Ignore Blocks" in content
    assert "This content should appear in llms-full.txt." in content
    assert "This content after the ignore block should appear" in content
    assert "Another Section" in content
    assert "Final content that should appear." in content

    # Check that ignored block content is not present
    assert "This content should be ignored and not appear" not in content
    assert "Section Ignored" not in content
    assert "Another ignored block with multiple lines." not in content
    assert "Item 1 (ignored)" not in content
    assert "def ignored_function():" not in content


def test_manager_mark_page_ignored():
    """Test that manager can mark pages as ignored."""
    from sphinx_llms_txt import LLMSFullManager

    manager = LLMSFullManager()

    # Initially no pages are ignored
    assert len(manager.ignored_pages) == 0

    # Mark a page as ignored
    manager.mark_page_ignored("test_page")

    # Check that page is in ignored set
    assert "test_page" in manager.ignored_pages
    assert len(manager.ignored_pages) == 1

    # Mark another page as ignored
    manager.mark_page_ignored("another_page")

    # Check both pages are ignored
    assert "test_page" in manager.ignored_pages
    assert "another_page" in manager.ignored_pages
    assert len(manager.ignored_pages) == 2


def test_process_ignore_blocks_empty_blocks():
    """Test that empty ignore blocks are handled correctly."""
    processor = DocumentProcessor({}, None)

    content = """Content before.

.. llms-txt-ignore-start

.. llms-txt-ignore-end

Content after."""

    processed = processor._process_ignore_blocks(content)

    # Check that content remains
    assert "Content before." in processed
    assert "Content after." in processed

    # Check that we don't have excessive newlines
    lines = processed.strip().split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    assert len(non_empty_lines) == 2


def test_ignore_metadata_affects_both_files(basic_sphinx_app):
    """Test that :llms-txt-ignore: true affects both files."""
    app = basic_sphinx_app
    # Enable both llms.txt and llms-full.txt file generation
    app.config.llms_txt_file = True
    app.config.llms_txt_filename = "test-llms.txt"
    app.build()

    # Check if both output files were created
    llms_full_file = Path(app.outdir) / "test-llms-full.txt"
    llms_summary_file = Path(app.outdir) / "test-llms.txt"

    assert llms_full_file.exists(), f"Output file {llms_full_file} does not exist"
    assert llms_summary_file.exists(), f"Output file {llms_summary_file} does not exist"

    # Read the content of both files
    llms_full_content = llms_full_file.read_text()
    llms_summary_content = llms_summary_file.read_text()

    # Check that page with metadata ignore is excluded from llms-full.txt
    assert "Page Ignored by Metadata" not in llms_full_content
    assert "This page should not appear in llms-full.txt" not in llms_full_content

    # Check that page with metadata ignore is also excluded from llms.txt
    # This should NOT contain a link to the ignored page
    assert "Page Ignored by Metadata" not in llms_summary_content
    assert "page_ignored_metadata.html" not in llms_summary_content
