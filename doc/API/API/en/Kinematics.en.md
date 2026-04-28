# Kinematics

## Overview

The Kinematics module provides forward/inverse kinematics in Python by loading solver plugins at runtime.

Main interfaces:

- `KinematicError`
- `KinematicsResult`
- `KinematicsBase`
- `KdlKinematicsPlugin` (available when built with `ELITE_COMPILE_KIN_PLUGIN=ON`)
- `ClassLoader.createKinematicsInstance`

## Import

In the current version, newly added kinematics types are exported by the extension module:

```python
from elite_cs_sdk.elite_cs_sdk_python import (
    ClassLoader,
    KinematicsBase,
    KinematicsResult,
    KinematicError,
    KdlKinematicsPlugin,
)
```

## KinematicError Enum

```python
class KinematicError(Enum):
    OK
    SOLVER_NOT_ACTIVE
    NO_SOLUTION
```

## KinematicsResult

```python
class KinematicsResult:
    kinematic_error: KinematicError
```

## ClassLoader

### Constructor

```python
ClassLoader(lib_path: str)
```

- `lib_path`: absolute path to plugin shared library.

### Load plugin library

```python
loadLib() -> bool
```

### Check loaded state

```python
hasLoadedLib() -> bool
```

### Create kinematics instance

```python
createKinematicsInstance(derived_class_name: str) -> KinematicsBase | None
```

- `derived_class_name`: registered derived class name, e.g. `ELITE::KdlKinematicsPlugin`.

## KinematicsBase

### Set MDH parameters

```python
setMDH(alpha: list[float], a: list[float], d: list[float])
```

### Forward kinematics

```python
getPositionFK(joint_angles: list[float]) -> tuple[bool, list[float]]
```

Returns `(ok, pose)`.

### Inverse kinematics (single solution)

```python
getPositionIK(pose: list[float], near: list[float]) -> tuple[bool, list[float], KinematicsResult]
```

Returns `(ok, solution, result)`.

### Inverse kinematics (all solutions)

```python
getPositionIKAll(pose: list[float], near: list[float]) -> tuple[bool, list[list[float]], KinematicsResult]
```

Returns `(ok, solutions, result)`.

### Timeout

```python
setDefaultTimeout(timeout: float)
getDefaultTimeout() -> float
```

## KdlKinematicsPlugin

```python
KdlKinematicsPlugin()
```

Derived from `KinematicsBase`.

## Example

See:

- `examples/example_kinematics.py`

It demonstrates:

1. Reading DH parameters from Primary port;
2. Reading current joints/TCP from RTSI;
3. Creating solver with `ClassLoader.createKinematicsInstance`;
4. Running FK/IK.
