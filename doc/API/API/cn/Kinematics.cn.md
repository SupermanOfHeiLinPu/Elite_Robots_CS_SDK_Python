# Kinematics

## 简介

Kinematics 模块提供机器人的正逆运动学能力，包括：

- 通过 `ClassLoader` 动态加载运动学插件；
- 使用 `KinematicsBase` 执行 FK / IK / IK-All；
- 使用 `KinematicsResult` 和 `KinematicError` 获取求解状态。

当编译时开启 `ELITE_COMPILE_KIN_PLUGIN=ON`，会额外提供 `KdlKinematicsPlugin`。

## 导入

当前新增的 Kinematics 相关类型在扩展模块中导出，推荐导入方式如下：

```python
from elite_cs_sdk.elite_cs_sdk_python import (
    ClassLoader,
    KinematicsBase,
    KinematicsResult,
    KinematicError,
    KdlKinematicsPlugin,
)
```

## KinematicError 枚举

```python
class KinematicError(Enum):
    OK
    SOLVER_NOT_ACTIVE
    NO_SOLUTION
```

表示运动学求解状态。

## KinematicsResult 类

```python
class KinematicsResult:
    kinematic_error: KinematicError
```

用于返回 IK/FK 结果状态。

## ClassLoader 类

### 构造函数

```python
ClassLoader(lib_path: str)
```

- `lib_path`：插件动态库绝对路径。

### 加载插件

```python
loadLib() -> bool
```

- 加载插件动态库。

### 查询是否已加载

```python
hasLoadedLib() -> bool
```

### 创建运动学实例

```python
createKinematicsInstance(derived_class_name: str) -> KinematicsBase | None
```

- `derived_class_name`：注册的派生类名，例如 `ELITE::KdlKinematicsPlugin`。
- 返回值：创建成功返回实例，失败返回 `None`。

## KinematicsBase 类

### 设置 MDH 参数

```python
setMDH(alpha: list[float], a: list[float], d: list[float])
```

### 正运动学 FK

```python
getPositionFK(joint_angles: list[float]) -> tuple[bool, list[float]]
```

- 返回 `(ok, pose)`。

### 逆运动学 IK（单解）

```python
getPositionIK(pose: list[float], near: list[float]) -> tuple[bool, list[float], KinematicsResult]
```

- 返回 `(ok, solution, result)`。

### 逆运动学 IK（全解）

```python
getPositionIKAll(pose: list[float], near: list[float]) -> tuple[bool, list[list[float]], KinematicsResult]
```

- 返回 `(ok, solutions, result)`。

### 超时设置

```python
setDefaultTimeout(timeout: float)
getDefaultTimeout() -> float
```

## KdlKinematicsPlugin 类

```python
KdlKinematicsPlugin()
```

继承自 `KinematicsBase`。

## 使用示例

完整示例请参考：

- `examples/example_kinematics.py`

示例流程：

1. 通过 Primary 端口读取 `KinematicsInfo`（DH 参数）；
2. 通过 RTSI 读取当前关节与 TCP；
3. 通过 `ClassLoader.createKinematicsInstance` 创建插件实例；
4. 执行 FK / IK 并输出结果。
