# SetupSphinx.cmake - Find Sphinx for CI environments

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

    # Get Sphinx version
    execute_process(
        COMMAND ${SPHINX_EXECUTABLE} --version
        OUTPUT_VARIABLE SPHINX_VERSION_OUTPUT
        ERROR_VARIABLE SPHINX_VERSION_OUTPUT
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    message(STATUS "Found Sphinx: ${SPHINX_EXECUTABLE}")
    message(STATUS "${SPHINX_VERSION_OUTPUT}")

    # Export to parent scope
    set(SPHINX_EXECUTABLE "${SPHINX_EXECUTABLE}" PARENT_SCOPE)
endfunction()
