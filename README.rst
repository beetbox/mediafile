MediaFile: read and write audio files' tags in Python
=====================================================

.. image:: https://travis-ci.org/beetbox/mediafile.svg?branch=master
    :target: https://travis-ci.org/beetbox/mediafile

.. image:: http://img.shields.io/pypi/v/mediafile.svg
    :target: https://pypi.python.org/pypi/mediafile

MediaFile is a simple interface to the metadata tags for many audio file
formats. It wraps `Mutagen`_, a high-quality library for low-level tag
manipulation, with a high-level, format-independent interface for a common set
of tags.

.. _Mutagen: https://github.com/quodlibet/mutagen

Synopsis
--------

.. code:: python

  >>> f = MediaFile('Lucy.mp3')
  >>> f.title
  u'Lucy in the Sky with Diamonds'
  >>> f.artist = 'The Beatles'
  >>> f.save()

Authors
-------

MediaFile is part of the `beets`_ project. It was originally written by
`Adrian Sampson`_ and is now developed by the beets community. The license is
MIT.

.. _Adrian Sampson: https://github.com/sampsyo
.. _beets: https://github.com/beetbox/beets
.. _MIT: http://www.opensource.org/licenses/mit-license.php
