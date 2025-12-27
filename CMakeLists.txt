cmake_minimum_required(VERSION 3.12)
project(Vayunicus)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization is critical for LBM [cite: 46]
if(MSVC)
    add_compile_options(/O2 /fp:fast)
else()
    add_compile_options(-O3 -march=native -ffast-math)
endif()

# Define source files
set(SOURCES
    source/main.cpp
)

add_executable(VayunicusEngine ${SOURCES})

# Include the source directory for headers
target_include_directories(VayunicusEngine PRIVATE source)