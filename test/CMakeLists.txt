set(name ut-jcppy)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -gdwarf-2 -pedantic -Wall -Wextra -Werror -std=c++11")

set(schemas
  ${CMAKE_SOURCE_DIR}/schema/core.json
  ${CMAKE_SOURCE_DIR}/schema/deeply_nested.json
  ${CMAKE_SOURCE_DIR}/schema/dog.json
  ${CMAKE_SOURCE_DIR}/schema/nested_array.json
  ${CMAKE_SOURCE_DIR}/schema/nested.json
  ${CMAKE_SOURCE_DIR}/schema/plain_array.json
)

jcppy_generate(
  SOURCES generated_sources
  HEADERS generated_headers
  SNIPPET_DIR ${CMAKE_SOURCE_DIR}/snippet
  NAMESPACE jcppy::gen
  BOOST_THROW_EXCEPTION
  NOEXCEPT
  ${schemas}
)

add_executable(${name}
  ${generated_sources}
  main.cpp
  base64_decode.cpp
)

target_link_libraries(${name}
  gtest
  gtest_main
  ${Boost_DATE_TIME_LIBRARY}
)

add_test(unit-tests "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${name}")
add_test(style ${PYLINT_EXECUTABLE}
    --max-line-length 100
    --good-names i,j,k,ex,Run,_,__,o,oo,s
    ${CMAKE_SOURCE_DIR}/jcppy.py
)
