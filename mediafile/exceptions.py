"""Custom exceptions for MediaFile metadata handling."""


class UnreadableFileError(Exception):
    """Mutagen is not able to extract information from the file."""

    def __init__(self, filename, msg):
        Exception.__init__(self, msg if msg else repr(filename))


class FileTypeError(UnreadableFileError):
    """Reading this type of file is not supported.

    If passed the `mutagen_type` argument this indicates that the
    mutagen type is not supported by `Mediafile`.
    """

    def __init__(self, filename, mutagen_type=None):
        if mutagen_type is None:
            msg = "{0!r}: not in a recognized format".format(filename)
        else:
            msg = "{0}: of mutagen type {1}".format(repr(filename), mutagen_type)
        Exception.__init__(self, msg)


class MutagenError(UnreadableFileError):
    """Raised when Mutagen fails unexpectedly---probably due to a bug."""

    def __init__(self, filename, mutagen_exc):
        msg = "{0}: {1}".format(repr(filename), mutagen_exc)
        Exception.__init__(self, msg)


__all__ = ["UnreadableFileError", "FileTypeError", "MutagenError"]
