import base64

import mutagen
import mutagen.flac

from mediafile.utils import Image

from .base import ListStorageStyle


class VorbisImageStorageStyle(ListStorageStyle):
    """Store images in Vorbis comments. Both legacy COVERART fields and
    modern METADATA_BLOCK_PICTURE tags are supported. Data is
    base64-encoded. Values are `Image` objects.
    """

    formats = ["OggOpus", "OggTheora", "OggSpeex", "OggVorbis", "OggFlac"]

    def __init__(self):
        super().__init__(key="metadata_block_picture")
        self.as_type = bytes

    def fetch(self, mutagen_file):
        images = []
        if "metadata_block_picture" not in mutagen_file:
            # Try legacy COVERART tags.
            if "coverart" in mutagen_file:
                for data in mutagen_file["coverart"]:
                    images.append(Image(base64.b64decode(data)))
            return images
        for data in mutagen_file["metadata_block_picture"]:
            try:
                pic = mutagen.flac.Picture(base64.b64decode(data))
            except (TypeError, AttributeError):
                continue
            images.append(Image(data=pic.data, desc=pic.desc, type=pic.type))
        return images

    def store(self, mutagen_file, image_data):
        # Strip all art, including legacy COVERART.
        if "coverart" in mutagen_file:
            del mutagen_file["coverart"]
        if "coverartmime" in mutagen_file:
            del mutagen_file["coverartmime"]
        super().store(mutagen_file, image_data)

    def serialize(self, image):
        """Turn a Image into a base64 encoded FLAC picture block."""
        pic = mutagen.flac.Picture()
        pic.data = image.data
        pic.type = image.type_index
        pic.mime = image.mime_type
        pic.desc = image.desc or ""

        # Encoding with base64 returns bytes on both Python 2 and 3.
        # Mutagen requires the data to be a Unicode string, so we decode
        # it before passing it along.
        return base64.b64encode(pic.write()).decode("ascii")
