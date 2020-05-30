cmake_minimum_required(VERSION 3.16)
project(memcpy)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Debug)
add_definitions( -DSIZE=8000062 )
add_definitions( -DMEASURE_PER_RUN=10 )
add_definitions( -DNUM_THREADS=8 )
add_definitions( -DCOUNT_PER_THREAD=1000000 )

find_package (Threads)
add_executable(memcpy_block memcpy_block.cpp)
target_link_libraries (memcpy_block Threads::Threads)

add_executable(memcpy_shuffle memcpy_shuffle.cpp)
target_link_libraries (memcpy_shuffle Threads::Threads)

add_executable(atomics atomics.cpp)
target_link_libraries (atomics Threads::Threads)

