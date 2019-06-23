# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Rtags(CMakePackage):
    """RTags is a client/server application that indexes C/C++ code"""

    homepage = "https://github.com/Andersbakken/rtags/"
    url      = "https://andersbakken.github.io/rtags-releases/rtags-2.17.tar.gz"
    git      = 'https://github.com/Andersbakken/rtags.git'

    version('master', branch='master', depth=2, submodules=True)
    version('2.17', '95b24d7729678645a027d83be114d624')

    depends_on("llvm@3.3: +clang")
    depends_on("zlib")
    depends_on("openssl")
    depends_on("lua@5.3:")
    depends_on("bash-completion")
    depends_on("pkgconfig", type='build')
    depends_on("emacs", when='+emacs')

    variant('emacs', default=False, description='Enable generation of elisp files')

    patch("add_string_iterator_erase_compile_check.patch", when='@2.12')

    def cmake_args(self):
        args = ['-DCMAKE_EXPORT_COMPILE_COMMANDS=1', '-DRTAGS_NO_ELISP_FILES=%d'%(not '+emacs' in self.spec)]
        return args
