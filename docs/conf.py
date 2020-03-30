# -*- coding: utf-8 -*-

# Path to mediafile module for autodoc.
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
]

source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

project = 'MediaFile'
copyright = '2016, the beets project'
author = 'the beets project'

version = '0.5'
release = '0.5.0'

pygments_style = 'sphinx'
htmlhelp_basename = 'mediafiledoc'

# LaTeX output.
latex_documents = [
    (master_doc, 'MediaFile.tex', 'MediaFile Documentation',
     'the beets project', 'manual'),
]

# mapage output.
man_pages = [
    (master_doc, 'mediafile', 'MediaFile Documentation',
     [author], 1)
]
