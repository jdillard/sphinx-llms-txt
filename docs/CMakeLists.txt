# Find Sphinx
include(SetupSphinx)
setup_sphinx_environment()

set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR}/source)
set(SPHINX_BUILD ${CMAKE_BINARY_DIR})

# Build HTML documentation
add_custom_target(html
    COMMAND ${SPHINX_EXECUTABLE} -b html ${SPHINX_SOURCE} ${SPHINX_BUILD}/html
    VERBATIM
)

# Build markdown documentation
add_custom_target(markdown
    COMMAND ${SPHINX_EXECUTABLE} -b markdown ${SPHINX_SOURCE} ${SPHINX_BUILD}/markdown
    VERBATIM
)

# Build singlemarkdown documentation and rename to llms-full.txt
add_custom_target(singlemarkdown
    COMMAND ${SPHINX_EXECUTABLE} -b singlemarkdown ${SPHINX_SOURCE} ${SPHINX_BUILD}/singlemarkdown
    VERBATIM
)

# Build all formats
add_custom_target(docs ALL)
add_dependencies(docs html markdown singlemarkdown)
