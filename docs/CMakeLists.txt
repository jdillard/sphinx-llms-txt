# Find Sphinx
include(SetupSphinx)
setup_sphinx_environment()

set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR}/source)
set(SPHINX_BUILD ${CMAKE_BINARY_DIR})

# Build HTML documentation
add_custom_target(html
    COMMAND ${SPHINX_EXECUTABLE} -b html ${SPHINX_SOURCE} ${SPHINX_BUILD}
    COMMENT "Building HTML documentation"
    VERBATIM
)

# Build markdown documentation
add_custom_target(markdown
    COMMAND ${SPHINX_EXECUTABLE} -b markdown ${SPHINX_SOURCE} ${SPHINX_BUILD}
    COMMENT "Building Markdown documentation"
    VERBATIM
)

# Build reStructuredText documentation
add_custom_target(rst
    COMMAND ${SPHINX_EXECUTABLE} -b rst ${SPHINX_SOURCE} ${SPHINX_BUILD}
    COMMENT "Building reStructuredText documentation"
    VERBATIM
)
