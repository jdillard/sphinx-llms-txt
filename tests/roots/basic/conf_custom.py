"""Configuration file for the basic Sphinx project."""

project = "Test Project"
copyright = "2025, Test"
author = "Test"

extensions = [
    "sphinx_llms_txt",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]

# Configuration for sphinx-llms-txt
llms_txt_filename = "custom-name.txt"
llms_txt_verbose = True

# Master document
master_doc = "index"
