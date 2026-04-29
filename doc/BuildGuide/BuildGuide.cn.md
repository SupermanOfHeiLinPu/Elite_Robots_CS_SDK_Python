# 编译安装向导

## 依赖安装

### Ubuntu

```bash
sudo apt update

# 基础工具
sudo apt install -y build-essential cmake git python3 python3-pip

# SDK依赖
sudo apt install -y libboost-all-dev libssh-dev

# 运动学插件依赖（开启 ELITE_COMPILE_KIN_PLUGIN=ON 时建议安装）
sudo apt install -y libeigen3-dev liborocos-kdl-dev

# 当前工程 python_wheel 使用 --no-build-isolation，
# 需要在“你实际用于构建的 Python 环境”里预先安装以下包
python3 -m pip install --upgrade pip setuptools wheel build
python3 -m pip install pybind11 pybind11_stubgen
```

### Windows

使用 `vcpkg` 安装：

```bash
.\vcpkg install boost-asio
.\vcpkg install libssh
.\vcpkg install orocos-kdl
.\vcpkg install eigen3
.\vcpkg integrate install
```

可选：如果已经通过 vcpkg 安装了完整 boost，建议移除 vcpkg 的 python 相关包，避免优先使用 vcpkg 自带 python。

```bash
.\vcpkg remove python3 boost-parameter-python boost-python
.\vcpkg integrate install
```

安装 Python 打包相关组件：

```bash
python3 -m pip install --upgrade pip setuptools wheel build
python3 -m pip install pybind11 pybind11_stubgen
```

## 编译与安装

### 方案 A：常规方式（可联网）

```bash
cd <clone of this repository>

# 需先手动 clone/download Elite_Robots_CS_SDK。

cmake -S . -B build \
	-DELITE_CS_SDK_REPO=<Elite_Robots_CS_SDK 本地路径> \
	-DELITE_COMPILE_KIN_PLUGIN=ON

cmake --build build --target python_wheel

python3 -m pip install --force-reinstall dist/elite_cs_sdk-*.whl
```

### 方案 B：弱网/离线方式（推荐 CI 或内网）

```bash
cd <clone of this repository>

# 需先手动 clone/download Elite_Robots_CS_SDK。

cmake -S . -B build \
	-DELITE_CS_SDK_REPO=<Elite_Robots_CS_SDK 本地路径> \
	-DFETCHCONTENT_SOURCE_DIR_PYBIND11=<本地 pybind11 源码目录> \
	-DFETCHCONTENT_UPDATES_DISCONNECTED=ON \
	-DELITE_COMPILE_KIN_PLUGIN=ON \
	-DPython3_EXECUTABLE=$(which python3)

cmake --build build --target python_wheel

python3 -m pip install --force-reinstall dist/elite_cs_sdk-*.whl
```

### Windows 参考命令

```bash
cd <clone of this repository>

# 需先手动 clone/download Elite_Robots_CS_SDK。

cmake -S . -B build \
	-DELITE_CS_SDK_REPO=<Elite_Robots_CS_SDK 本地路径> \
	-DELITE_COMPILE_KIN_PLUGIN=ON

cmake --build build --config Release --target python_wheel

python -m pip install --force-reinstall dist/elite_cs_sdk-*.whl
```

## 说明

- `ELITE_CS_SDK_REPO` 为必填项，且必须是本地仓库路径。
- Elite_Robots_CS_SDK 不再由 CMake 自动拉取，需提前手动下载。
- `python_wheel` 目标会自动触发扩展编译、`.pyi` 生成和 wheel 打包。
- 运动学插件开启后，wheel 打包阶段会自动复制 `libelite_kdl_kinematics` 到包目录。
- 如果只想验证扩展编译，不打包 wheel，可执行：

```bash
cmake --build build -j1 --target elite_cs_sdk_python
```