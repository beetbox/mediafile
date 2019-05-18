MediaFile: elegant audio file tagging
=====================================

MediaFile is a simple interface to the metadata tags for many audio file
formats. It wraps `Mutagen`_, a high-quality library for low-level tag
manipulation, with a high-level, format-independent interface for a common set
of tags.

It currently supports MP3 files (ID3 tags), AAC files (as tagged by iTunes) as
well as FLAC, Ogg, Monkey's Audio, WavPack, and Musepack.

MediaFile attempts to always return a usable value (i.e., it never returns
``None`` or throws an exception when a tag is accessed). If a tag is not
present, an empty and false value of the appropriate type -- such as zero or
the empty string -- is returned.

.. _Mutagen: https://github.com/quodlibet/mutagen

.. toctree::
   :maxdepth: 2

Supported Metadata Fields
-------------------------
The metadata schema is generally based on MusicBrainz' schema with similar naming. MediaFile supports:

* basic fields like ``title``, ``album``, ``artist`` and ``albumartist``,
* sorting variants like ``albumartist_sort`` and ``composer_sort``,
* identifiers like ``asin`` or ``mb_releasegroupid``,
* dates like the release ``year``, ``month`` and ``day`` with convenience wrapper ``date``,
* detailed metadata like ``language`` or ``media``,
* ``lyrics``,
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
able to interact with beets.


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


Changelog
---------

* **v0.1.0**: MediaFile is now synchronised with the embedded version released
  with Beets v1.4.8.
