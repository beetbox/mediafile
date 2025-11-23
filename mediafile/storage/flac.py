import mutagen.flac

from mediafile.utils import Image

from .base import ListStorageStyle


class FlacImageStorageStyle(ListStorageStyle):
    """Converts between ``mutagen.flac.Picture`` and ``Image`` instances."""

    formats = ["FLAC"]

    def __init__(self):
        super().__init__(key="")

    def fetch(self, mutagen_file):
        return mutagen_file.pictures

    def deserialize(self, flac_picture):
        return Image(
            data=flac_picture.data, desc=flac_picture.desc, type=flac_picture.type
        )

    def store(self, mutagen_file, pictures):
        """``pictures`` is a list of mutagen.flac.Picture instances."""
        mutagen_file.clear_pictures()
        for pic in pictures:
            mutagen_file.add_picture(pic)

    def serialize(self, image):
        """Turn a Image into a mutagen.flac.Picture."""
        pic = mutagen.flac.Picture()
        pic.data = image.data
        pic.type = image.type_index
        pic.mime = image.mime_type
        pic.desc = image.desc or ""
        return pic

    def delete(self, mutagen_file):
        """Remove all images from the file."""
        mutagen_file.clear_pictures()
