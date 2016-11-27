# -*- coding: utf-8 -*-
# This file is part of mediafile.
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

"""Some common functionality for mediafile tests."""
from __future__ import division, absolute_import, print_function

import os
import tempfile
import shutil
import sys


# Test resources path.
RSRC = os.path.join(os.path.dirname(__file__), 'rsrc').encode('utf8')

# OS feature test.
HAVE_SYMLINK = sys.platform != 'win32'


# Convenience methods for setting up a temporary sandbox directory for tests
# that need to interact with the filesystem.
class TempDirMixin(object):
    """Text mixin for creating and deleting a temporary directory.
    """

    def create_temp_dir(self):
        """Create a temporary directory and assign it into `self.temp_dir`.
        Call `remove_temp_dir` later to delete it.
        """
        path = tempfile.mkdtemp()
        if not isinstance(path, bytes):
            path = path.encode('utf8')
        self.temp_dir = path

    def remove_temp_dir(self):
        """Delete the temporary directory created by `create_temp_dir`.
        """
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
