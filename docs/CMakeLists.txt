# Find Sphinx
include(SetupSphinx)
setup_sphinx_environment()

# Add builder targets
add_sphinx_builder(html)
add_sphinx_builder(markdown)
add_sphinx_builder(singlemarkdown)
