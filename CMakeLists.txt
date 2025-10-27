cmake_minimum_required(VERSION 3.15)
project(SphinxLLMsTxt VERSION 1.0.0 LANGUAGES NONE)

# Add CMake module path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

# Add documentation
add_subdirectory(docs)
