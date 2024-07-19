cmake_minimum_required(VERSION 3.10)
project(lg)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -Wall -pthread -fpic ${CMAKE_CPP_FLAGS}")

set(SOVERSION 1)

set(prefix "/usr/local")
set(exec_prefix "${prefix}")
set(bindir "${exec_prefix}/bin")
set(includedir "${prefix}/include")
set(libdir "${prefix}/lib")
set(mandir "${prefix}/man")

set(CC "${CROSS_PREFIX}gcc")
set(CXX "${CROSS_PREFIX}g++")
set(AR "${CROSS_PREFIX}ar")
set(RANLIB "${CROSS_PREFIX}ranlib")
set(SIZE "${CROSS_PREFIX}size")
set(STRIP "${CROSS_PREFIX}strip")
set(SHLIB "${CC} -shared")
set(STRIPLIB "${STRIP} --strip-unneeded")
set(PYTHON "python3")

SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

include_directories(
    ${CMAKE_FIND_ROOT_PATH}/usr/include
    ${CMAKE_FIND_ROOT_PATH}/usr/include/${CMAKE_LIBRARY_ARCHITECTURE}
)

set(OBJ_LGPIO
    lgCtx.c
    lgDbg.c
    lgErr.c
    lgGpio.c
    lgHdl.c
    lgI2C.c
    lgNotify.c
    lgPthAlerts.c
    lgPthTx.c
    lgSerial.c
    lgSPI.c
    lgThread.c
    lgUtil.c
)

set(OBJ_RGPIO
    rgpio.c
    lgCfg.c
    lgErr.c
    lgDbg.c
    lgMD5.c
)

set(OBJ_RGPIOD
    lgCfg.c
    lgCmd.c
    lgExec.c
    lgFile.c
    lgMD5.c
    lgPthSocket.c
    lgScript.c
)

set(OBJ_RGS
    lgCmd.c
    lgCfg.c
    lgDbg.c
    lgErr.c
    lgMD5.c
)

set(DOCS
    DOC/src/defs/rgs.def
    DOC/src/defs/rgpiod.def
    DOC/src/defs/permits.def
    DOC/src/defs/scripts.def
    lgpio.h
    rgpio.h
)

add_library(lgpio SHARED ${OBJ_LGPIO})
set_target_properties(lgpio PROPERTIES
    VERSION ${SOVERSION}
    SOVERSION ${SOVERSION}
)
add_custom_command(TARGET lgpio POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E create_symlink ${CMAKE_SHARED_LIBRARY_PREFIX}lgpio.${SOVERSION} ${CMAKE_SHARED_LIBRARY_PREFIX}lgpio
    COMMAND ${STRIP} $<TARGET_FILE:lgpio>
    COMMAND ${SIZE} $<TARGET_FILE:lgpio>
)

add_library(rgpio SHARED ${OBJ_RGPIO})
set_target_properties(rgpio PROPERTIES
    VERSION ${SOVERSION}
    SOVERSION ${SOVERSION}
)
add_custom_command(TARGET rgpio POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E create_symlink ${CMAKE_SHARED_LIBRARY_PREFIX}rgpio.${SOVERSION} ${CMAKE_SHARED_LIBRARY_PREFIX}rgpio
    COMMAND ${STRIP} $<TARGET_FILE:rgpio>
    COMMAND ${SIZE} $<TARGET_FILE:rgpio>
)

add_executable(rgpiod rgpiod.c ${OBJ_RGPIOD})
add_custom_command(TARGET rgpiod POST_BUILD
    COMMAND ${STRIP} $<TARGET_FILE:rgpiod>
    COMMAND ${SIZE} $<TARGET_FILE:rgpiod>
)
target_link_libraries(rgpiod lgpio pthread rt)

add_executable(rgs rgs.c ${OBJ_RGS})
add_custom_command(TARGET rgs POST_BUILD
    COMMAND ${STRIP} $<TARGET_FILE:rgs>
    COMMAND ${SIZE} $<TARGET_FILE:rgs>
)

add_custom_target(docs DEPENDS ${DOCS})

# add_custom_target(all DEPENDS lgpio rgpio rgpiod rgs docs)

install(TARGETS lgpio DESTINATION ${libdir})
install(TARGETS rgpio DESTINATION ${libdir})
install(TARGETS rgpiod DESTINATION ${bindir})
install(TARGETS rgs DESTINATION ${bindir})

install(FILES lgpio.h rgpio.h DESTINATION ${includedir})
install(FILES DOC/src/defs/rgs.def DOC/src/defs/rgpiod.def DOC/src/defs/permits.def DOC/src/defs/scripts.def DESTINATION ${mandir})
