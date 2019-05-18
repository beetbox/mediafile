#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of MediaFile.
# Copyright 2016, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

from __future__ import division, absolute_import, print_function

import os
from os import path
import sys
from setuptools.dist import Distribution
from setuptools import setup, Command


class CustomDistribution(Distribution):
    def __init__(self, *args, **kwargs):
        self.sdist_requires = None
        Distribution.__init__(self, *args, **kwargs)

    def get_finalized_command(self, command, create=1):
        cmd_obj = self.get_command_obj(command, create)
        cmd_obj.ensure_finalized()
        return cmd_obj

    def export_live_eggs(self, env=False):
        """Adds all of the eggs in the current environment to PYTHONPATH."""
        path_eggs = [p for p in sys.path if p.endswith('.egg')]

        command = self.get_finalized_command("egg_info")
        egg_base = path.abspath(command.egg_base)

        unique_path_eggs = set(path_eggs + [egg_base])

        os.environ['PYTHONPATH'] = ':'.join(unique_path_eggs)


class test(Command):  # noqa: ignore=N801
    """Command to run tox."""

    description = "run tox tests"

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        self.tox_args = ''

    def finalize_options(self):
        pass

    def run(self):
        # Install test dependencies if needed.
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)

        # Add eggs to PYTHONPATH. We need to do this to ensure our eggs are
        # seen by Tox.
        self.distribution.export_live_eggs()

        import shlex
        import tox

        parsed_args = shlex.split(self.tox_args)
        result = tox.cmdline(args=parsed_args)

        sys.exit(result)


def _read(filename):
    relative_path = path.join(path.dirname(__file__), filename)
    return open(relative_path).read()


setup(
    name='mediafile',
    version='0.1.0',
    description='low-level audio tag interface',
    author='Adrian Sampson',
    author_email='adrian@radbox.org',
    url='https://github.com/beetbox/mediafile',
    license='MIT',
    platforms='ALL',
    long_description=_read('README.rst'),
    long_description_content_type='text/x-rst',

    py_modules=[
        'mediafile',
    ],

    install_requires=[
        'six>=1.9',
        'mutagen>=1.33',
    ] + (['enum34>=1.0.4'] if sys.version_info < (3, 4, 0) else []),

    tests_require=[
        'tox',
    ],

    cmdclass={
        'test': test,
    },

    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    distclass=CustomDistribution
)
