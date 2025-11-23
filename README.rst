MediaFile: read and write audio files' tags in Python
=====================================================

.. image:: https://github.com/beetbox/mediafile/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/beetbox/mediafile/actions

.. image:: https://img.shields.io/pypi/v/mediafile.svg
    :target: https://pypi.python.org/pypi/mediafile

MediaFile is a simple interface to the metadata tags for many audio file
formats. It wraps Mutagen_, a high-quality library for low-level tag
manipulation, with a high-level, format-independent interface for a common set
of tags.

.. _mutagen: https://github.com/quodlibet/mutagen

Synopsis
--------

MediaFile is available `on PyPI`_. Install it by typing ``pip install
mediafile``. It works on Python 3.10 or later. Then:

.. code-block:: python

    from mediafile import MediaFile

    f = MediaFile("Lucy.mp3")
    f.title
    "Lucy in the Sky with Diamonds"
    f.artist = "The Beatles"
    f.save()

.. _on pypi: https://pypi.python.org/pypi/mediafile

Documentation
-------------

See the `full documentation`_.

.. _full documentation: https://mediafile.readthedocs.io/

Authors
-------

MediaFile is part of the beets_ project. It was originally written by `Adrian
Sampson`_ and is now developed by the beets community. The license is MIT.

.. _adrian sampson: https://github.com/sampsyo

.. _beets: https://github.com/beetbox/beets

.. _mit: https://www.opensource.org/licenses/mit-license.php
