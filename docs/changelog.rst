Changelog
---------

Upcoming
''''''''

- Dropped support for Python 3.7 and 3.8
- Added minimal contribution guidelines to CONTRIBUTING.md
- Changed project linter and formatter from ``flake8`` to ``ruff``. Reformatted 
    the codebase with ``ruff``.
- Moved changelog into its own file, ``changelog.rst``. Also added github workflow
    for automatic changelog reminders.

v0.13.0
'''''''

- Add a mapping compatible with Plex and ffmpeg for the "original date"
  fields.
- Remove an unnecessary dependency on `six`.
- Replace `imghdr` with `filetype` to support Python 3.13.

v0.12.0
'''''''

- Add the multiple-valued properties ``artists_credit``, ``artists_sort``,
  ``albumartists_credit``, and ``albumartists_sort``.

v0.11.0
'''''''

- List-valued properties now return ``None`` instead of an empty list when the
  underlying tags are missing altogether.

v0.10.1
'''''''

- Fix a test failure that arose with Mutagen 1.46.
- Require Python 3.7 or later.

v0.10.0
'''''''

- Add the multiple-valued properties ``albumtypes``, ``catalognums`` and
  ``languages``.
- The ``catalognum`` property now refers to additional file tags named
  ``CATALOGID`` and ``DISCOGS_CATALOG`` (but only for reading, not writing).
- The multi-valued ``albumartists`` property now refers to additional file
  tags named ``ALBUM_ARTIST`` and ``ALBUM ARTISTS``. (The latter
  is used only for reading.)
- The ``ListMediaField`` class now doesn't concatenate multiple lists if
  found. The first available tag is used instead, like with other kinds of
  fields.

v0.9.0
''''''

- Add the properties ``bitrate_mode``, ``encoder_info`` and
  ``encoder_settings``.

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
