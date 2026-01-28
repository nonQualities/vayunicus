cmake_minimum_required(VERSION 3.10)
project(vayunicus)

# Use C++17 (Required for your project)
set(CMAKE_CXX_STANDARD 17)

# Create the executable by listing the 3 specific files we created
add_executable(vayunicus
    source/main.cpp
    source/engine/solver.cpp
    source/io/dataLoader.cpp
)

# Allow us to use #include "Engine/Solver.hpp"
target_include_directories(vayunicus PRIVATE source)