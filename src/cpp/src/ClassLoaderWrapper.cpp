// SPDX-License-Identifier: MIT
// Copyright (c) 2025, Elite Robots.
#include "ClassLoaderWrapper.hpp"

#if __has_include(<Elite/ClassLoader.hpp>) && __has_include(<Elite/KinematicsBase.hpp>)
#include <Elite/ClassLoader.hpp>
#include <Elite/KinematicsBase.hpp>
#define ELITE_PY_HAS_CLASS_LOADER 1
#else
#define ELITE_PY_HAS_CLASS_LOADER 0
#endif

namespace py = pybind11;

void bindClassLoader(py::module_& m) {
#if ELITE_PY_HAS_CLASS_LOADER
	using namespace ELITE;

	py::class_<ClassLoader>(m, "ClassLoader", "Runtime class loader for plugin libraries.")
		.def(py::init<const std::string&>(), py::arg("lib_path"),
			 R"doc(
				Construct a class loader.

				Args:
					lib_path (str): Absolute path of plugin library.
			)doc")
		.def("loadLib", &ClassLoader::loadLib,
			 R"doc(
				Load plugin library.

				Returns:
					bool: True if the library is loaded successfully.
			)doc")
		.def("hasLoadedLib", &ClassLoader::hasLoadedLib,
			 R"doc(
				Check whether plugin library has been loaded.

				Returns:
					bool: True if loaded.
			)doc")
		.def(
			"createKinematicsInstance",
			[](ClassLoader& self, const std::string& derived_class_name) -> KinematicsBaseSharedPtr {
				auto instance = self.createUniqueInstance<KinematicsBase>(derived_class_name);
				if (!instance) {
					return nullptr;
				}
				return KinematicsBaseSharedPtr(std::move(instance));
			},
			py::arg("derived_class_name"),
			R"doc(
				Create an instance by class name, using KinematicsBase as the default base type.

				This is equivalent to C++:
					createUniqueInstance<KinematicsBase>(derived_class_name)

				Args:
					derived_class_name (str): Registered class name.

				Returns:
					KinematicsBase: Created instance, or None if failed.
			)doc");
#else
	(void)m;
#endif
}