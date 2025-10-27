# Setup Sphinx environment
include(SetupSphinx)
setup_sphinx_environment()

set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source)
set(BUILD_DIR ${CMAKE_SOURCE_DIR}/build)

# Custom target to build HTML documentation
add_custom_target(html
    COMMAND ${SPHINX_EXECUTABLE} -b html
    ${SOURCE_DIR} ${BUILD_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    VERBATIM
)

# Custom target to build markdown documentation
add_custom_target(markdown
    COMMAND ${SPHINX_EXECUTABLE} -b markdown
    ${SOURCE_DIR} ${BUILD_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    VERBATIM
)

# Target to build both in parallel (when invoked with cmake --build . --target docs)
add_custom_target(docs)
add_dependencies(docs html markdown)
