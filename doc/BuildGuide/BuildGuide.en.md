# Compilation and Installation Guide

## Dependency Installation

### Ubuntu

```bash
sudo apt update

# Base tools
sudo apt install -y build-essential cmake git python3 python3-pip

# SDK dependencies
sudo apt install -y libboost-all-dev libssh-dev

# Kinematics plugin dependencies (recommended when ELITE_COMPILE_KIN_PLUGIN=ON)
sudo apt install -y libeigen3-dev liborocos-kdl-dev

# The python_wheel target uses --no-build-isolation.
# Install these packages in the same Python environment used for build.
python3 -m pip install --upgrade pip setuptools wheel build
python3 -m pip install pybind11 pybind11_stubgen
```

### Windows

Install with `vcpkg`:

```bash
.\vcpkg install boost-asio
.\vcpkg install libssh
.\vcpkg integrate install
```

Optional: if full boost has already been installed via vcpkg, it is recommended to remove vcpkg Python-related packages to avoid using vcpkg Python by mistake during build.

```bash
.\vcpkg remove python3 boost-parameter-python boost-python
.\vcpkg integrate install
```

Install Python packaging dependencies:

```bash
python3 -m pip install --upgrade pip setuptools wheel build
python3 -m pip install pybind11 pybind11_stubgen
```

## Build and Install

### Option A: Standard flow (online)

```bash
cd <clone of this repository>

cmake -S . -B build \
	-DELITE_CS_SDK_REPO=<local path or repository url of Elite_Robots_CS_SDK> \
	-DELITE_COMPILE_KIN_PLUGIN=ON

cmake --build build -j$(nproc) --target python_wheel

python3 -m pip install --force-reinstall dist/elite_cs_sdk-*.whl
```

### Option B: Weak-network / offline flow

```bash
cd <clone of this repository>

cmake -S . -B build \
	-DFETCHCONTENT_SOURCE_DIR_PYBIND11=<local pybind11 source dir> \
	-DFETCHCONTENT_SOURCE_DIR_ELITE_CS_SDK=<local Elite_Robots_CS_SDK source dir> \
	-DFETCHCONTENT_UPDATES_DISCONNECTED=ON \
	-DELITE_COMPILE_KIN_PLUGIN=ON \
	-DPython3_EXECUTABLE=$(which python3)

cmake --build build -j1 --target python_wheel

python3 -m pip install --force-reinstall dist/elite_cs_sdk-*.whl
```

### Windows reference commands

```bash
cd <clone of this repository>

cmake -S . -B build \
	-DELITE_CS_SDK_REPO=<local path or repository url of Elite_Robots_CS_SDK> \
	-DELITE_COMPILE_KIN_PLUGIN=ON

cmake --build build --config Release --target python_wheel

python -m pip install --force-reinstall dist/elite_cs_sdk-*.whl
```

## Notes

- `python_wheel` triggers extension build, `.pyi` generation, and wheel packaging.
- With kinematics plugin enabled, `libelite_kdl_kinematics` is copied into package directory during wheel packaging.
- To verify only extension build without packaging, run:

```bash
cmake --build build -j1 --target elite_cs_sdk_python
```