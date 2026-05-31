# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) Spack Project Developers. See COPYRIGHT file for details.
# --------------------------------------------------------------------------------------------------
from spack_repo.builtin.build_systems.cmake import CMakePackage

from spack.package import *


class Lyra(CMakePackage):
    """A simple to use, composable, header-only command-line parser for C++11 and beyond."""

    homepage = "https://github.com/bfgroup/Lyra"
    url = "https://github.com/bfgroup/Lyra/releases/download/1.7.0/lyra-1.7.0.tar.bz2"
    license("BSL-1.0")

    version("1.7.0", sha256="2a4cbf23e4a4b9c33dd25df11e5017e0647575b45b8b4a42349ab754f670b853")
    depends_on("cmake@3.12:", type="build")

    def test(self):
        test_src = join_path(self.package_dir, "test")
        test_dir = self.test_suite.current_test_data_dir

        install_tree(test_src, test_dir)

        with working_dir(test_dir):
            cmake = which("cmake")
            cmake(
                "-S",
                ".",
                "-B",
                "build",
                "-DCMAKE_PREFIX_PATH={0}".format(self.prefix),
                "-DCMAKE_CXX_STANDARD=11",
                "-DCMAKE_CXX_STANDARD_REQUIRED=ON",
            )
            cmake("--build", "build")

            Executable("./build/test_lyra")()
