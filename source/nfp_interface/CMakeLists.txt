cmake_minimum_required ( VERSION 2.8 )

project (libnfporb_interface)

# set(CMAKE_CXX_FLAGS "/MD /EHsc") #Microsoft Visual C++ compiler
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC") #Linux with GCC or Clang 
# For other compilers you should consult its documentation.

set(PATH_PYTHON $ENV{PYTHONPATH}) # replace $ENV{PYTHONPATH} with absolute path to your Python installation
set(PATH_BOOST $ENV{BOOST_ROOT}) # replace $ENV{BOOST_ROOT} with absolute path to your Boost installation

link_directories(${PATH_PYTHON}/libs) 
include_directories(${PATH_BOOST})
include_directories(${PATH_PYTHON}/include)

# Set output library name without "lib" prefix
set(LIBRARY_OUTPUT_NAME "nfporb_interface")

add_library ( ${PROJECT_NAME} SHARED
	libnfporb_interface.cpp
)

# Set output library name using set_target_properties
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME ${LIBRARY_OUTPUT_NAME})
# This will generate a shared library file named nfporb_interface.so
# on Linux systems or libnfporb_interface.dll on Windows systems,
# depending on the platform.