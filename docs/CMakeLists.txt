# Find Sphinx
include(SetupSphinx)
setup_sphinx_environment()

set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR}/source)
set(SPHINX_BUILD ${CMAKE_BINARY_DIR})

# Function to add a Sphinx builder target
function(add_sphinx_builder builder_name)
    add_custom_target(${builder_name}
        COMMAND ${SPHINX_EXECUTABLE} -b ${builder_name} ${SPHINX_SOURCE} ${SPHINX_BUILD}/${builder_name}
        VERBATIM
    )
endfunction()

# Add builder targets
add_sphinx_builder(html)
add_sphinx_builder(markdown)
add_sphinx_builder(singlemarkdown)
