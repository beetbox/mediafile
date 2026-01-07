# This file is part of MediaFile.
# Copyright 2016, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.


from .deprecation import deprecate_imports
from .exceptions import FileTypeError, MediaFileError, MutagenError, UnreadableFileError
from .mediafile import MediaFile
from .utils import Image

__all__ = [
    "MediaFile",
    "Image",
    "MediaFileError",
    "UnreadableFileError",
    "FileTypeError",
    "MutagenError",
]


def __getattr__(name: str):
    """Handle deprecated imports."""

    return deprecate_imports(
        __name__,
        {
            # Constants
            "TYPES": "mediafile.constants",
            "ImageType": "mediafile.constants",
            # Fields
            "MediaField": "mediafile.fields",
            "CoverArtField": "mediafile.fields",
            "DateField": "mediafile.fields",
            "DateItemField": "mediafile.fields",
            "ImageListField": "mediafile.fields",
            "ListMediaField": "mediafile.fields",
            "QNumberField": "mediafile.fields",
            # Storage
            "StorageStyle": "mediafile.storage",
            "ListStorageStyle": "mediafile.storage",
            "SoundCheckStorageStyleMixin": "mediafile.storage",
            "ASFStorageStyle": "mediafile.storage",
            "ASFImageStorageStyle": "mediafile.storage",
            "APEv2ImageStorageStyle": "mediafile.storage",
            "FlacImageStorageStyle": "mediafile.storage",
            "MP3StorageStyle": "mediafile.storage",
            "MP3SoundCheckStorageStyle": "mediafile.storage",
            "MP3DescStorageStyle": "mediafile.storage",
            "MP3PeopleStorageStyle": "mediafile.storage",
            "MP3SlashPackStorageStyle": "mediafile.storage",
            "MP3ImageStorageStyle": "mediafile.storage",
            "MP3ListStorageStyle": "mediafile.storage",
            "MP3UFIDStorageStyle": "mediafile.storage",
            "MP3ListDescStorageStyle": "mediafile.storage",
            "MP4StorageStyle": "mediafile.storage",
            "MP4TupleStorageStyle": "mediafile.storage",
            "MP4BoolStorageStyle": "mediafile.storage",
            "MP4SoundCheckStorageStyle": "mediafile.storage",
            "MP4ImageStorageStyle": "mediafile.storage",
            "MP4ListStorageStyle": "mediafile.storage",
            "VorbisImageStorageStyle": "mediafile.storage",
            # Utils
            "image_mime_type": "mediafile.utils",
            "image_extension": "mediafile.utils",
            "loadfile": "mediafile.utils",
            "mutagen_call": "mediafile.utils",
            "update_filething": "mediafile.utils",
            "sc_encode": "mediafile.utils",
            "sc_decode": "mediafile.utils",
            "safe_cast": "mediafile.utils",
        },
        name,
    )
