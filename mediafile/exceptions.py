"""Custom exceptions for MediaFile metadata handling."""

from __future__ import annotations


class MediaFileError(Exception):
    """Base exception for all MediaFile-related errors."""

    def __init__(
        self,
        message: str,
        filename: str | None = None,
    ):
        self.filename = filename
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.filename:
            return f"{self.filename}: {self.message}"
        return self.message

    def __str__(self) -> str:
        return self._format_message()


class UnreadableFileError(MediaFileError):
    """Raised when Mutagen cannot extract information from the file."""

    def __init__(
        self,
        filename: str,
        message: str,
    ):
        super().__init__(
            message,
            filename,
        )


class FileTypeError(UnreadableFileError):
    """Reading this type of file is not supported.

    If passed the `mutagen_type` argument this indicates that the
    mutagen type is not supported by `Mediafile`.
    """

    def __init__(
        self,
        filename: str,
        mutagen_type: str | None = None,
    ):
        if mutagen_type is None:
            msg = "File is not in a recognized format"
        else:
            msg = f"File type '{mutagen_type}' is not supported"

        super().__init__(filename, msg)


class MutagenError(UnreadableFileError):
    """Raised when Mutagen fails unexpectedly, likely due to a bug."""

    mutagen_exception: Exception

    def __init__(self, filename: str, mutagen_exception: Exception):
        self.mutagen_exception = mutagen_exception
        message = f"Mutagen internal error: {mutagen_exception}"
        super().__init__(filename, message)


__all__ = ["UnreadableFileError", "FileTypeError", "MutagenError"]
