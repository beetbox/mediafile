import mutagen
import mutagen.asf

from .base import ListStorageStyle


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
        super(ASFImageStorageStyle, self).__init__(key="WM/Picture")

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
