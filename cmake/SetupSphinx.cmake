# SetupSphinx.cmake - Automatically setup Sphinx documentation environment

# Function to setup Python virtual environment and install Sphinx
function(setup_sphinx_environment)
    set(VENV_DIR "${CMAKE_SOURCE_DIR}/.docs-venv")
    set(REQUIREMENTS_FILE "${CMAKE_SOURCE_DIR}/docs/requirements.txt")
    set(REQUIREMENTS_STAMP "${CMAKE_BINARY_DIR}/requirements.stamp")

    set(PYTHON_EXECUTABLE "python3")
    set(VENV_PYTHON "${VENV_DIR}/bin/python")
    set(VENV_SPHINX "${VENV_DIR}/bin/sphinx-build")

    # Check if Python is available
    find_program(PYTHON_CMD ${PYTHON_EXECUTABLE})

    if(NOT PYTHON_CMD)
        message(FATAL_ERROR "Python not found.")
    endif()

    # Get Python version
    execute_process(
        COMMAND ${PYTHON_CMD} --version
        OUTPUT_VARIABLE PYTHON_VERSION_OUTPUT
        ERROR_VARIABLE PYTHON_VERSION_OUTPUT
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    message(STATUS "Found Python: ${PYTHON_CMD}")
    message(STATUS "Python version: ${PYTHON_VERSION_OUTPUT}")

    # Check if virtual environment exists
    if(NOT EXISTS "${VENV_PYTHON}")
        message(STATUS "Creating Python virtual environment at: ${VENV_DIR}")
        execute_process(
            COMMAND ${PYTHON_CMD} -m venv "${VENV_DIR}"
            RESULT_VARIABLE VENV_RESULT
            OUTPUT_VARIABLE VENV_OUTPUT
            ERROR_VARIABLE VENV_ERROR
        )

        if(NOT VENV_RESULT EQUAL 0)
            message(FATAL_ERROR "Failed to create virtual environment:\n${VENV_ERROR}")
        endif()
    else()
        message(STATUS "Using existing virtual environment at: ${VENV_DIR}")
    endif()

    # Check if requirements.txt has changed
    set(NEED_INSTALL FALSE)

    if(NOT EXISTS "${REQUIREMENTS_STAMP}")
        set(NEED_INSTALL TRUE)
        message(STATUS "No requirements stamp found - will install dependencies")
    elseif("${REQUIREMENTS_FILE}" IS_NEWER_THAN "${REQUIREMENTS_STAMP}")
        set(NEED_INSTALL TRUE)
        message(STATUS "requirements.txt has changed - will reinstall dependencies")
    else()
        message(STATUS "Dependencies are up to date")
    endif()

    # Install/upgrade pip and dependencies only if needed
    if(NEED_INSTALL)
        message(STATUS "Upgrading pip...")
        execute_process(
            COMMAND "${VENV_PYTHON}" -m pip install --upgrade pip
            OUTPUT_QUIET
            ERROR_QUIET
        )

        # Install the package in editable mode along with other dependencies
        if(EXISTS "${REQUIREMENTS_FILE}")
            message(STATUS "Installing Sphinx dependencies from requirements.txt...")
            execute_process(
                COMMAND "${VENV_PYTHON}" -m pip install -r "${REQUIREMENTS_FILE}"
                RESULT_VARIABLE PIP_INSTALL_RESULT
                OUTPUT_VARIABLE PIP_OUTPUT
                ERROR_VARIABLE PIP_ERROR
            )

            if(NOT PIP_INSTALL_RESULT EQUAL 0)
                message(WARNING "Failed to install some dependencies:\n${PIP_ERROR}")
            else()
                message(STATUS "Sphinx dependencies installed successfully")
            endif()
        else()
            message(WARNING "requirements.txt not found at: ${REQUIREMENTS_FILE}")
        endif()

        # Install the package in editable mode
        message(STATUS "Installing sphinx-llms-txt in editable mode...")
        execute_process(
            COMMAND "${VENV_PYTHON}" -m pip install -e "${CMAKE_SOURCE_DIR}"
            RESULT_VARIABLE PIP_INSTALL_RESULT
            OUTPUT_VARIABLE PIP_OUTPUT
            ERROR_VARIABLE PIP_ERROR
        )

        if(NOT PIP_INSTALL_RESULT EQUAL 0)
            message(WARNING "Failed to install sphinx-llms-txt:\n${PIP_ERROR}")
        else()
            message(STATUS "sphinx-llms-txt installed successfully")
            # Create stamp file to mark successful installation
            file(TOUCH "${REQUIREMENTS_STAMP}")
        endif()
    endif()

    # Verify Sphinx installation
    if(EXISTS "${VENV_SPHINX}")
        execute_process(
            COMMAND "${VENV_SPHINX}" --version
            OUTPUT_VARIABLE SPHINX_VERSION_OUTPUT
            ERROR_VARIABLE SPHINX_VERSION_OUTPUT
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        message(STATUS "Sphinx installed: ${SPHINX_VERSION_OUTPUT}")

        # Export Sphinx executable to parent scope
        set(Sphinx_FOUND TRUE PARENT_SCOPE)
        set(SPHINX_EXECUTABLE "${VENV_SPHINX}" PARENT_SCOPE)
    else()
        message(FATAL_ERROR "Sphinx installation failed - sphinx-build not found")
    endif()

    # Export Python executable to parent scope
    set(SPHINX_PYTHON_EXECUTABLE "${VENV_PYTHON}" PARENT_SCOPE)

    # Track requirements.txt changes to trigger CMake reconfiguration
    configure_file(
        "${REQUIREMENTS_FILE}"
        "${CMAKE_BINARY_DIR}/requirements.txt.tracked"
        COPYONLY
    )
endfunction()
