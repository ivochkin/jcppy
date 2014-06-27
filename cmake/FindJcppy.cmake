# Copyright (c) 2014 Stanislav Ivochkin <isn@extrn.org>
# License: MIT (see LICENSE for details).

include(CMakeParseArguments)
include(FindPackageHandleStandardArgs)

find_program(JCPPY_EXECUTABLE jcppy.py
  NAMES jcppy
  PATHS ${JCPPY_ROOT}
  DOC "Path to jcppy executable"
)

find_package(PythonInterp REQUIRED)

if(JCPPY_EXECUTABLE)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${JCPPY_EXECUTABLE} --version
    ERROR_VARIABLE JCPPY_VERSION
    OUTPUT_VARIABLE JCPPY_VERSION
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_STRIP_TRAILING_WHITESPACE
  )
  string(REGEX REPLACE ".* (.*)" "\\1" JCPPY_VERSION ${JCPPY_VERSION})
endif()

set(JCPPY "${JCPPY_EXECUTABLE} (found version \"${JCPPY_VERSION}\")")
find_package_handle_standard_args(jcppy DEFAULT_MSG JCPPY JCPPY_EXECUTABLE JCPPY_VERSION)


function(JCPPY_GENERATE)
  list(APPEND PARAMS
    SOURCES
    HEADERS
    NAMESPACE
    OUTPUT_DIR
    SNIPPET_DIR
  )

  list(APPEND OPTIONS
    NOEXCEPT
    BOOST_THROW_EXCEPTION
  )

  cmake_parse_arguments(JCPPY "${OPTIONS}" "${PARAMS}" "" ${ARGN})

  list(LENGTH JCPPY_UNPARSED_ARGUMENTS ARGC)
  if(NOT ${ARGC})
    message(SEND_ERROR "Error: JCPPY_GENERATE() called without any schema files")
    return()
  endif()

  set(INVOKE_ARGS)

  if(NOT JCPPY_SOURCES)
    message(SEND_ERROR "No output variable set for generated sources")
  endif()

  if(NOT JCPPY_HEADERS)
    message(SEND_ERROR "No output variable set for generated headers")
  endif()

  if(JCPPY_NAMESPACE)
    set(INVOKE_ARGS  ${INVOKE_ARGS} --namespace ${JCPPY_NAMESPACE})
  endif()

  if(JCPPY_NOEXCEPT)
    set(INVOKE_ARGS ${INVOKE_ARGS} --noexcept)
  endif()

  if(JCPPY_BOOST_THROW_EXCEPTION)
    set(INVOKE_ARGS ${INVOKE_ARGS} --boost-throw-exception)
  endif()

  if(NOT JCPPY_OUTPUT_DIR)
    set(JCPPY_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR})
  endif()

  if(JCPPY_SNIPPET_DIR)
    set(INVOKE_ARGS ${INVOKE_ARGS} --snippet-dir ${JCPPY_SNIPPET_DIR})
  endif()

  file(MAKE_DIRECTORY ${JCPPY_OUTPUT_DIR})

  set(${JCPPY_SOURCES})
  set(${JCPPY_HEADERS})
  foreach(i ${JCPPY_UNPARSED_ARGUMENTS})
    get_filename_component(ABS ${i} ABSOLUTE)
    get_filename_component(WE ${i} NAME_WE)

    list(APPEND ${JCPPY_HEADERS} "${JCPPY_OUTPUT_DIR}/${WE}.h")
    list(APPEND ${JCPPY_SOURCES} "${JCPPY_OUTPUT_DIR}/${WE}.cpp")

    add_custom_command(
      OUTPUT "${JCPPY_OUTPUT_DIR}/${WE}.h"
             "${JCPPY_OUTPUT_DIR}/${WE}.cpp"
      COMMAND ${PYTHON_EXECUTABLE}
      ARGS ${JCPPY_EXECUTABLE} ${INVOKE_ARGS} --output-dir ${JCPPY_OUTPUT_DIR} ${ABS}
      DEPENDS ${i}
      DEPENDS ${JCPPY_EXECUTABLE}
      COMMENT "Running jccpy generator on ${i}"
      VERBATIM
    )
  endforeach()

  set_source_files_properties(${${SRCS}} ${${HDRS}} PROPERTIES GENERATED TRUE)
  set(${JCPPY_SOURCES} ${${JCPPY_SOURCES}} PARENT_SCOPE)
  set(${JCPPY_HEADERS} ${${JCPPY_HEADERS}} PARENT_SCOPE)
endfunction()
