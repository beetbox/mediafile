MediaFile: elegant audio file tagging
=====================================

MediaFile is a simple interface to the metadata tags for many audio file
formats. It wraps `Mutagen`_, a high-quality library for low-level tag
manipulation, with a high-level, format-independent interface for a common set
of tags.

It currently supports MP3 files (ID3 tags), AAC files (as tagged by iTunes) as
well as FLAC, Ogg, Monkey's Audio, WavPack, and Musepack.

If a tag does not exist, MediaFile will return ``None`` instead of throwing
an exception.

.. _Mutagen: https://github.com/quodlibet/mutagen

.. toctree::
   :maxdepth: 2

Supported Metadata Fields
-------------------------
The metadata schema is generally based on MusicBrainz' schema with similar naming. MediaFile supports:

* basic fields like ``title``, ``album``, ``artist`` and ``albumartist``,
* sorting variants like ``albumartist_sort`` and ``composer_sort``,
* plural/list variants like ``artists`` and ``albumartists``,
* identifiers like ``asin``, ``isrc`` or ``mb_releasegroupid``,
* dates like the release ``year``, ``month`` and ``day`` with convenience wrapper ``date``,
* detailed metadata like ``language`` or ``media``,
* ``lyrics``, ``copyright``, ``url``
* calculated metadata like ``bpm`` (beats per minute) and ``r128_track_gain`` (ReplayGain),
* embedded images (e.g. album art),
* file metadata like ``bitrate`` and ``length``.

Compatibility
-------------
The ID3 and MPEG-4 test cases were created with iTunes and the FLAC and Ogg test
cases were created (mostly) with
`MediaRage`_. The Monkey's Audio tags were mainly fabricated using the open-source
`Tag`_. Thus, MediaFile's tag support most closely aligns with those three applications.
Some open questions remain about how to most compatibly tag files. In particular, some
fields MediaFile supports don't seem standardized among FLAC/Ogg taggers:

.. _MediaRage: http://www.chaoticsoftware.com/ProductPages/MediaRage.html
.. _Tag: http://sbooth.org/Tag/

  * ``grouping`` and ``lyrics``: couldn't find anyone who supports these in a
    cursory search; MediaFile uses the keys ``grouping`` and ``lyrics``
  * ``tracktotal`` and ``disctotal``: we use the keys ``tracktotal``, ``totaltracks``,
    and ``trackc`` all to mean the same thing
  * ``year``: this field appears both as a part of the ``date`` field and on its own
    using some taggers; both are supported

For fields that have multiple possible storage keys, MediaFile optimizes for
interoperability: it accepts _any_ of the possible storage keys and writes _all_
of them. This may result in duplicated information in the tags, but it ensures
that other players with slightly divergent opinions on tag names will all be
able to interact with `beets`_.


Images (album art) are stored in the standard ways for ID3 and MPEG-4. For all
other formats, images are stored with the `METADATA_BLOCK_PICTURE standard <MBP>`_ from Vorbis
Comments. The older `COVERART`_ unofficial format is also read but is not written.

.. _MBP: http://wiki.xiph.org/VorbisComment#METADATA_BLOCK_PICTURE
.. _COVERART: http://wiki.xiph.org/VorbisComment#Unofficial_COVERART_field_.28deprecated.29

.. currentmodule:: mediafile

MediaFile Class
---------------

.. autoclass:: MediaFile

    .. automethod:: __init__
    .. automethod:: fields
    .. automethod:: readable_fields
    .. automethod:: save
    .. automethod:: update

Exceptions
----------

.. autoclass:: UnreadableFileError
.. autoclass:: FileTypeError
.. autoclass:: MutagenError

Internals
---------

.. autoclass:: MediaField

    .. automethod:: __init__

.. autoclass:: StorageStyle
    :members:


Examples
--------

To add cover art to a MediaFile:

.. code:: python

    from mediafile import MediaFile, Image, ImageType

    image_file = "cover.jpg"
    with open(image_file, 'rb') as f:
        cover = f.read()
        cover = Image(data=cover, desc=u'album cover', type=ImageType.front)
    f = MediaFile("file.mp3)
    f.images = [cover]
    f.save()


To copy tags from one MediaFile to another:

.. code:: python

    from mediafile import MediaFile

    f = MediaFile("file1.mp3")
    g = MediaFile("file2.mp3")

    for field in f.fields():
        try:
            setattr(g, field, getattr(f, field))
        except:
            pass

    g.save()


Changelog
---------

v0.8.1
''''''

- Fix a regression in v0.8.0 that caused a crash on Python versions below 3.8.

v0.8.0
''''''

- MediaFile now requires Python 3.6 or later.
- Added support for Wave (`.wav`) files.

v0.7.0
''''''

- Mutagen 1.45.0 or later is now required.
- MediaFile can now use file-like objects (instead of just the filesystem, via
  filenames).

v0.6.0
''''''

- Enforce a minimum value for SoundCheck gain values.

v0.5.0
''''''

- Refactored the distribution to use `Flit`_.

.. _Flit: https://flit.readthedocs.io/

v0.4.0
''''''

- Added a ``barcode`` field.
- Added new tag mappings for ``albumtype`` and ``albumstatus``.

v0.3.0
''''''

- Fixed tests for compatibility with Mutagen 1.43.
- Fix the MPEG-4 tag mapping for the ``label`` field to use the right
  capitalization.

v0.2.0
''''''

- R128 gain tags are now stored in Q7.8 integer format, as per
  `the relevant standard`_.
- Added an ``mb_workid`` field.
- The Python source distribution now includes an ``__init__.py`` file that
  makes it easier to run the tests.

.. _the relevant standard: https://tools.ietf.org/html/rfc7845.html#page-25

v0.1.0
''''''

This is the first independent release of MediaFile.
It is now synchronised with the embedded version released with `beets`_ v1.4.8.

.. _beets: https://beets.io
