cmake_minimum_required(VERSION 3.10)
project(vtsh C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(vtsh vtsh.c)
target_compile_options(vtsh PRIVATE -Wall -Wextra)
