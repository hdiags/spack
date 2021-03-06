# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import re

import llnl.util.tty as tty

from spack.architecture import OperatingSystem
from spack.util.module_cmd import module


class Cnl(OperatingSystem):
    """ Compute Node Linux (CNL) is the operating system used for the Cray XC
    series super computers. It is a very stripped down version of GNU/Linux.
    Any compilers found through this operating system will be used with
    modules. If updated, user must make sure that version and name are
    updated to indicate that OS has been upgraded (or downgraded)
    """

    def __init__(self):
        name = 'cnl'
        version = self._detect_crayos_version()
        super(Cnl, self).__init__(name, version)
        self.modulecmd = module

    def __str__(self):
        return self.name + str(self.version)

    def _detect_crayos_version(self):
        output = module("avail", "PrgEnv-cray")
        matches = re.findall(r'PrgEnv-cray/(\d+).\d+.\d+', output)
        major_versions = set(matches)
        latest_version = max(major_versions)
        return latest_version

    def arguments_to_detect_version_fn(self, paths):
        import spack.compilers

        command_arguments = []
        for compiler_name in spack.compilers.supported_compilers():
            cmp_cls = spack.compilers.class_for_compiler_name(compiler_name)

            # If the compiler doesn't have a corresponding
            # Programming Environment, skip to the next
            if cmp_cls.PrgEnv is None:
                continue

            if cmp_cls.PrgEnv_compiler is None:
                tty.die('Must supply PrgEnv_compiler with PrgEnv')

            compiler_id = spack.compilers.CompilerID(self, compiler_name, None)
            detect_version_args = spack.compilers.DetectVersionArgs(
                id=compiler_id, variation=(None, None),
                language='cc', path='cc'
            )
            command_arguments.append(detect_version_args)
        return command_arguments

    def detect_version(self, detect_version_args):
        import spack.compilers
        modulecmd = self.modulecmd
        compiler_name = detect_version_args.id.compiler_name
        compiler_cls = spack.compilers.class_for_compiler_name(compiler_name)
        output = modulecmd('avail', compiler_cls.PrgEnv_compiler)
        version_regex = r'(%s)/([\d\.]+[\d])' % compiler_cls.PrgEnv_compiler
        matches = re.findall(version_regex, output)
        version = tuple(version for _, version in matches)
        compiler_id = detect_version_args.id
        value = detect_version_args._replace(
            id=compiler_id._replace(version=version)
        )
        return value, None

    def make_compilers(self, compiler_id, paths):
        import spack.spec
        name = compiler_id.compiler_name
        cmp_cls = spack.compilers.class_for_compiler_name(name)
        compilers = []
        for v in compiler_id.version:
            comp = cmp_cls(
                spack.spec.CompilerSpec(name + '@' + v),
                self, "any",
                ['cc', 'CC', 'ftn'], [cmp_cls.PrgEnv, name + '/' + v])

            compilers.append(comp)
        return compilers
