import struct

import mutagen
import mutagen.asf

from mediafile.utils import Image

from .base import ListStorageStyle


def _unpack_asf_image(data):
    """Unpack image data from a WM/Picture tag. Return a tuple
    containing the MIME type, the raw image data, a type indicator, and
    the image's description.

    This function is treated as "untrusted" and could throw all manner
    of exceptions (out-of-bounds, etc.). We should clean this up
    sometime so that the failure modes are well-defined.
    """
    type, size = struct.unpack_from("<bi", data)
    pos = 5
    mime = b""
    while data[pos : pos + 2] != b"\x00\x00":
        mime += data[pos : pos + 2]
        pos += 2
    pos += 2
    description = b""
    while data[pos : pos + 2] != b"\x00\x00":
        description += data[pos : pos + 2]
        pos += 2
    pos += 2
    image_data = data[pos : pos + size]
    return (mime.decode("utf-16-le"), image_data, type, description.decode("utf-16-le"))


def _pack_asf_image(mime, data, type=3, description=""):
    """Pack image data for a WM/Picture tag."""
    tag_data = struct.pack("<bi", type, len(data))
    tag_data += mime.encode("utf-16-le") + b"\x00\x00"
    tag_data += description.encode("utf-16-le") + b"\x00\x00"
    tag_data += data
    return tag_data


class ASFStorageStyle(ListStorageStyle):
    """A general storage style for Windows Media/ASF files."""

    formats = ["ASF"]

    def deserialize(self, data):
        if isinstance(data, mutagen.asf.ASFBaseAttribute):
            data = data.value
        return data


class ASFImageStorageStyle(ListStorageStyle):
    """Store images packed into Windows Media/ASF byte array attributes.
    Values are `Image` objects.
    """

    formats = ["ASF"]

    def __init__(self):
        super().__init__(key="WM/Picture")

    def deserialize(self, asf_picture):
        mime, data, type, desc = _unpack_asf_image(asf_picture.value)
        return Image(data, desc=desc, type=type)

    def serialize(self, image):
        pic = mutagen.asf.ASFByteArrayAttribute()
        pic.value = _pack_asf_image(
            image.mime_type,
            image.data,
            type=image.type_index,
            description=image.desc or "",
        )
        return pic
