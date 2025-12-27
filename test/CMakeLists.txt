# Parent project does not export its library target, so this CML implicitly
# depends on being added from it, i.e. the testing is done only from the build
# tree and is not feasible from an install location

project(vayunicusTests LANGUAGES CXX)

# ---- Dependencies ----

find_package(Catch2 REQUIRED)
include(Catch)

# ---- Tests ----

add_executable(vayunicus_test source/vayunicus_test.cpp)
target_link_libraries(
    vayunicus_test PRIVATE
    vayunicus_lib
    Catch2::Catch2WithMain
)
target_compile_features(vayunicus_test PRIVATE cxx_std_17)

catch_discover_tests(vayunicus_test)

# ---- End-of-file commands ----

add_folders(Test)
