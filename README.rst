MediaFile: a simple low-level audio tag interface
=================================================

.. image:: https://travis-ci.org/beetbox/mediafile.svg?branch=master
    :target: https://travis-ci.org/beetbox/mediafile

.. image:: http://img.shields.io/pypi/v/mediafile.svg
    :target: https://pypi.python.org/pypi/mediafile

Handles low-level interfacing for files' tags. Wraps Mutagen to
automatically detect file types and provide a unified interface for a
useful subset of music files' tags.

Usage
-----

.. code:: python

  >>> f = MediaFile('Lucy.mp3')
  >>> f.title
  u'Lucy in the Sky with Diamonds'
  >>> f.artist = 'The Beatles'
  >>> f.save()

Internally ``MediaFile`` uses ``MediaField`` descriptors to access the
data from the tags. In turn ``MediaField`` uses a number of
``StorageStyle`` strategies to handle format specific logic.

Author
------

Confuse is being developed by `Adrian Sampson`_ and was originally made to
power `beets`_.

.. _Adrian Sampson: https://github.com/sampsyo
.. _beets: https://github.com/beetbox/beets
