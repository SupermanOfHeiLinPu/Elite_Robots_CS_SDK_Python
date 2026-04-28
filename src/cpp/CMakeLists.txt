cmake_minimum_required(VERSION 3.14)
project(elite_cs_sdk_python LANGUAGES CXX)

include(FetchContent)

execute_process(
  COMMAND git config --get remote.origin.url
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  OUTPUT_VARIABLE GIT_REMOTE_URL
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

if(GIT_REMOTE_URL MATCHES "gitee.com")
  if (NOT DEFINED ELITE_CS_SDK_REPO)
    set(ELITE_CS_SDK_REPO "https://gitee.com/elite-robots/Elite_Robots_CS_SDK.git")
  endif()
  set(PYBIND11_REPO "https://gitee.com/mirrors/pybind11.git")
else()
  if (NOT DEFINED ELITE_CS_SDK_REPO)
    set(ELITE_CS_SDK_REPO "https://github.com/Elite-Robots/Elite_Robots_CS_SDK.git")
  endif()
  set(PYBIND11_REPO "https://github.com/pybind/pybind11.git")
endif()

# Check for macOS patch file and set PATCH_COMMAND accordingly
set(MACOS_FIX_PATCH "${CMAKE_SOURCE_DIR}/macos_fixes.patch")
if(EXISTS "${MACOS_FIX_PATCH}")
  message(STATUS "Applying macOS fixes patch: ${MACOS_FIX_PATCH}")
  set(ELITE_SDK_PATCH_CMD git apply "${MACOS_FIX_PATCH}")
else()
  message(STATUS "macos_fixes.patch not found, skipping patch step.")
  set(ELITE_SDK_PATCH_CMD "")
endif()


FetchContent_Declare(
  pybind11
  GIT_REPOSITORY ${PYBIND11_REPO}
  GIT_TAG stable
)
FetchContent_MakeAvailable(pybind11)

FetchContent_Declare(
  elite_cs_sdk
  GIT_REPOSITORY ${ELITE_CS_SDK_REPO}
  GIT_TAG main
  PATCH_COMMAND ${ELITE_SDK_PATCH_CMD}
)
FetchContent_MakeAvailable(elite_cs_sdk)

set(ELITE_SDK_SRC_DIR ${elite_cs_sdk_SOURCE_DIR} PARENT_SCOPE)

if(TARGET elite-cs-series-sdk_SHARED)
  set(ELITE_SDK_SHARED_TARGET elite-cs-series-sdk_SHARED)
elseif(TARGET elite_cs_series_sdk_SHARED)
  set(ELITE_SDK_SHARED_TARGET elite_cs_series_sdk_SHARED)
else()
  message(FATAL_ERROR "Could not find SDK shared target: elite-cs-series-sdk_SHARED or elite_cs_series_sdk_SHARED")
endif()

set(ELITE_SDK_SHARED_TARGET ${ELITE_SDK_SHARED_TARGET} PARENT_SCOPE)

file(GLOB_RECURSE BINDING_CPP_SOURCES
  CONFIGURE_DEPENDS
  "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp"
)

file(GLOB_RECURSE BINDING_HEADERS
  CONFIGURE_DEPENDS
  "${CMAKE_CURRENT_SOURCE_DIR}/src/*.hpp"
)

set(BINDING_SOURCES
  ${BINDING_CPP_SOURCES}
  ${BINDING_HEADERS}
)

pybind11_add_module(elite_cs_sdk_python
  ${BINDING_SOURCES}
)

target_link_libraries(elite_cs_sdk_python PRIVATE ${ELITE_SDK_SHARED_TARGET})

set(ELITE_KDL_PLUGIN_INCLUDE_DIR
  "${elite_cs_sdk_SOURCE_DIR}/plugin/kinematics/KdlKinematicsPlugin/include"
)

if(TARGET elite_kdl_kinematics)
  target_include_directories(elite_cs_sdk_python PRIVATE "${ELITE_KDL_PLUGIN_INCLUDE_DIR}")
  target_link_libraries(elite_cs_sdk_python PRIVATE elite_kdl_kinematics)

  # Some environments provide Eigen include dirs without exporting Eigen3::Eigen into this scope.
  find_package(Eigen3 QUIET)

  if(TARGET Eigen3::Eigen)
    target_link_libraries(elite_cs_sdk_python PRIVATE Eigen3::Eigen)
  endif()

  if(DEFINED EIGEN3_INCLUDE_DIR)
    target_include_directories(elite_cs_sdk_python SYSTEM PRIVATE ${EIGEN3_INCLUDE_DIR})
  endif()

  if(DEFINED EIGEN3_INCLUDE_DIRS)
    target_include_directories(elite_cs_sdk_python SYSTEM PRIVATE ${EIGEN3_INCLUDE_DIRS})
  endif()

  if(DEFINED Eigen3_INCLUDE_DIRS)
    target_include_directories(elite_cs_sdk_python SYSTEM PRIVATE ${Eigen3_INCLUDE_DIRS})
  endif()

  if(EXISTS "/usr/include/eigen3")
    target_include_directories(elite_cs_sdk_python SYSTEM PRIVATE /usr/include/eigen3)
  endif()

  if(TARGET orocos-kdl)
    target_link_libraries(elite_cs_sdk_python PRIVATE orocos-kdl)
  endif()

  target_compile_definitions(elite_cs_sdk_python PRIVATE ELITE_PY_BIND_KDL_KINEMATICS_PLUGIN=1)
endif()

add_dependencies(elite_cs_sdk_python ${ELITE_SDK_SHARED_TARGET})

# Correctly handle suffixes and RPATH for macOS
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
  set(ELITE_PY_SDK_SUFFIX ".pyd")
  set(ELITE_INSTALL_RPATH "") # No RPATH on Windows
elseif(APPLE)
  set(ELITE_PY_SDK_SUFFIX ".so")
  # Use @loader_path for macOS RPATH, so the .so can find the .dylib
  set(ELITE_INSTALL_RPATH "@loader_path")
else() # Linux
  set(ELITE_PY_SDK_SUFFIX ".so")
  set(ELITE_INSTALL_RPATH "$ORIGIN")
endif()

set_target_properties(elite_cs_sdk_python PROPERTIES
  CXX_STANDARD 17
  CXX_STANDARD_REQUIRED YES
  BUILD_WITH_INSTALL_RPATH TRUE
  INSTALL_RPATH "${ELITE_INSTALL_RPATH}"
  OUTPUT_NAME "elite_cs_sdk_python"
  SUFFIX "${ELITE_PY_SDK_SUFFIX}"
)
