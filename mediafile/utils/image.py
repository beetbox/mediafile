# Cover art and other images.

import logging

import filetype

from mediafile.constants import ImageType

log = logging.getLogger(__name__)


def image_mime_type(data):
    """Return the MIME type of the image data (a bytestring)."""
    return filetype.guess_mime(data)


def image_extension(data):
    ext = filetype.guess_extension(data)
    # imghdr returned "tiff", so we should keep returning it with filetype.
    return ext if ext != "tif" else "tiff"


class Image:
    """Structure representing image data and metadata that can be
    stored and retrieved from tags.

    The structure has four properties.
    * ``data``  The binary data of the image
    * ``desc``  An optional description of the image
    * ``type``  An instance of `ImageType` indicating the kind of image
    * ``mime_type`` Read-only property that contains the mime type of
                    the binary data
    """

    def __init__(self, data, desc=None, type=None):
        assert isinstance(data, bytes)
        if desc is not None:
            assert isinstance(desc, str)
        self.data = data
        self.desc = desc
        if isinstance(type, int):
            try:
                type = list(ImageType)[type]
            except IndexError:
                log.debug("ignoring unknown image type index %s", type)
                type = ImageType.other
        self.type = type

    @property
    def mime_type(self):
        if self.data:
            return image_mime_type(self.data)

    @property
    def type_index(self):
        if self.type is None:
            # This method is used when a tag format requires the type
            # index to be set, so we return "other" as the default value.
            return 0
        return self.type.value
