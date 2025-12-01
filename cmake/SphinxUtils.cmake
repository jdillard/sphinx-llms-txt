# Sphinx related utilities

set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR}/source)
set(SPHINX_BUILD ${CMAKE_BINARY_DIR})

# Function to find Sphinx in the system
function(setup_sphinx_environment)
    # Find sphinx-build executable in system
    find_program(SPHINX_EXECUTABLE
        NAMES sphinx-build
        DOC "Sphinx documentation generator"
    )

    if(NOT SPHINX_EXECUTABLE)
        message(FATAL_ERROR "sphinx-build not found. Please install Sphinx.")
    endif()

    # Export to parent scope
    set(SPHINX_EXECUTABLE "${SPHINX_EXECUTABLE}" PARENT_SCOPE)
endfunction()

# Function to add a Sphinx builder target
function(add_sphinx_builder builder_name)
    add_custom_target(${builder_name}
        COMMAND ${SPHINX_EXECUTABLE} -b ${builder_name} ${SPHINX_SOURCE} ${SPHINX_BUILD}/${builder_name}
        VERBATIM
    )
endfunction()
