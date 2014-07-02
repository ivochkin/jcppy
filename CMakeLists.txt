cmake_minimum_required(VERSION 2.8)
project(jcppy)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
enable_testing()

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR})

add_subdirectory(external/gtest)
include_directories(SYSTEM external/gtest/include)
include_directories(SYSTEM external/rapidjson/include)

find_package(Threads REQUIRED)
link_libraries(${CMAKE_THREAD_LIBS_INIT})

find_package(Boost COMPONENTS date_time REQUIRED)
link_libraries(${Boost_DATE_TIME_LIBRARY})
include_directories(SYSTEM ${Boost_INCLUDE_DIRS})

find_package(PythonInterp REQUIRED)

find_program(PYLINT_EXECUTABLE pylint REQUIRED)
find_package_handle_standard_args(pylint DEFAULT_MSG PYLINT_EXECUTABLE)

set(JCPPY_ROOT ${CMAKE_CURRENT_SOURCE_DIR})
find_package(Jcppy REQUIRED)

add_subdirectory(test)

install(PROGRAMS jcppy.py RENAME jcppy DESTINATION bin)
install(FILES cmake/FindJcppy.cmake DESTINATION share/cmake/Modules)
install(DIRECTORY snippet DESTINATION share/jcppy)
