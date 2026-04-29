// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Elite Robots.
#include "KinematicsWrapper.hpp"

#include <pybind11/stl.h>

#ifndef ELITE_STATIC_LIBRARY
#define ELITE_STATIC_LIBRARY
#endif
#include <Elite/KinematicsBase.hpp>

#if defined(ELITE_PY_BIND_KDL_KINEMATICS_PLUGIN)
#include <KdlKinematicsPlugin.hpp>
#endif

namespace py = pybind11;

void bindKinematics(py::module_& m) {
    using namespace ELITE;

    py::enum_<KinematicError>(m, "KinematicError", py::arithmetic())
        .value("OK", KinematicError::OK)
        .value("SOLVER_NOT_ACTIVE", KinematicError::SOLVER_NOT_ACTIVE)
        .value("NO_SOLUTION", KinematicError::NO_SOLUTION)
        .export_values();

    py::class_<KinematicsResult>(m, "KinematicsResult")
        .def(py::init<>())
        .def_readwrite("kinematic_error", &KinematicsResult::kinematic_error, "Error code that indicates the type of failure.");

    py::class_<KinematicsBase, KinematicsBaseSharedPtr>(m, "KinematicsBase", "Base interface for kinematics solvers.")
        .def("setMDH", &KinematicsBase::setMDH, py::arg("alpha"), py::arg("a"), py::arg("d"),
             R"doc(
                Set robot MDH parameters.

                Args:
                    alpha (list): MDH alpha parameter
                    a (list): MDH a parameter
                    d (list): MDH d parameter
            )doc")
        .def(
            "getPositionFK",
            [](const KinematicsBase& self, const vector6d_t& joint_angles) {
                vector6d_t poses{};
                bool ok = self.getPositionFK(joint_angles, poses);
                return py::make_tuple(ok, poses);
            },
            py::arg("joint_angles"),
            R"doc(
                Compute forward kinematics.

                Args:
                    joint_angles (list): Joint states.

                Returns:
                    tuple: (ok, poses)
            )doc")
        .def(
            "getPositionIK",
            [](const KinematicsBase& self, const vector6d_t& pose, const vector6d_t& near) {
                vector6d_t solution{};
                KinematicsResult result{};
                bool ok = self.getPositionIK(pose, near, solution, result);
                return py::make_tuple(ok, solution, result);
            },
            py::arg("pose"), py::arg("near"),
            R"doc(
                Compute inverse kinematics and return one solution close to `near`.

                Args:
                    pose (list): Target end-effector pose [x, y, z, rx, ry, rz].
                    near (list): Initial guess for IK.

                Returns:
                    tuple: (ok, solution, result)
            )doc")
        .def(
            "getPositionIKAll",
            [](const KinematicsBase& self, const vector6d_t& pose, const vector6d_t& near) {
                std::vector<vector6d_t> solutions;
                KinematicsResult result{};
                bool ok = self.getPositionIK(pose, near, solutions, result);
                return py::make_tuple(ok, solutions, result);
            },
            py::arg("pose"), py::arg("near"),
            R"doc(
                Compute inverse kinematics and return all valid solutions.

                Args:
                    pose (list): Target end-effector pose [x, y, z, rx, ry, rz].
                    near (list): Initial guess for IK.

                Returns:
                    tuple: (ok, solutions, result)
            )doc")
        .def(
            "setDefaultTimeout",
            [](KinematicsBase& self, double timeout) {
                self.setDefaultTimeout(timeout);
            },
            py::arg("timeout"),
            R"doc(Set the default timeout in seconds.)doc")
        .def(
            "getDefaultTimeout",
            [](const KinematicsBase& self) {
                return self.getDefaultTimeout();
            },
            R"doc(Get the default timeout in seconds.)doc");

#if defined(ELITE_PY_BIND_KDL_KINEMATICS_PLUGIN)
    py::class_<KdlKinematicsPlugin, KinematicsBase, std::shared_ptr<KdlKinematicsPlugin>>(
    m, "KdlKinematicsPlugin", "KDL-based kinematics plugin implementation.");
#endif
}
