cmake_minimum_required(VERSION 3.16.0 FATAL_ERROR)
project("multiBlink")

add_subdirectory(../wiring-repka/wiringRP ${CMAKE_BINARY_DIR}/wrp)

add_executable(multiBlink mblink.c)
target_link_libraries(multiBlink PRIVATE wiringrp)

add_executable(button button.c)
target_link_libraries(button PRIVATE wiringrp)

add_executable(mbutton mbutton.c)
target_link_libraries(mbutton PRIVATE wiringrp)

add_executable(mtool mtool.c)
target_link_libraries(mtool PRIVATE wiringrp)