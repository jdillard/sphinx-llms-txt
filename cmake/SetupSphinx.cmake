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

    # Export to parent scope
    set(SPHINX_EXECUTABLE "${SPHINX_EXECUTABLE}" PARENT_SCOPE)
endfunction()
