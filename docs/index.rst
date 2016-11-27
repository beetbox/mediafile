MediaFile: elegant audio file tagging
=====================================

MediaFile is a simple interface to the metadata tags for many audio file
formats. It wraps `Mutagen`_, a high-quality library for low-level tag
manipulation, with a high-level, format-independent interface for a common set
of tags.

.. _Mutagen: https://github.com/quodlibet/mutagen

.. toctree::
   :maxdepth: 2

.. currentmodule:: mediafile

MediaFile Class
---------------

.. autoclass:: MediaFile
    :members: save, delete, fields, readable_fields, update

Exceptions
----------

.. autoclass:: UnreadableFileError
.. autoclass:: FileTypeError
.. autoclass:: MutagenError
