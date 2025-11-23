import mutagen.mp4

from mediafile.utils import Image

from .base import ListStorageStyle, SoundCheckStorageStyleMixin, StorageStyle


class MP4StorageStyle(StorageStyle):
    """A general storage style for MPEG-4 tags."""

    formats = ["MP4"]

    def serialize(self, value):
        value = super().serialize(value)
        if self.key.startswith("----:") and isinstance(value, str):
            value = value.encode("utf-8")
        return value


class MP4TupleStorageStyle(MP4StorageStyle):
    """A style for storing values as part of a pair of numbers in an
    MPEG-4 file.
    """

    def __init__(self, key, index=0, **kwargs):
        super().__init__(key, **kwargs)
        self.index = index

    def deserialize(self, mutagen_value):
        items = mutagen_value or []
        packing_length = 2
        return list(items) + [0] * (packing_length - len(items))

    def get(self, mutagen_file):
        value = super().get(mutagen_file)[self.index]
        if value == 0:
            # The values are always present and saved as integers. So we
            # assume that "0" indicates it is not set.
            return None
        else:
            return value

    def set(self, mutagen_file, value):
        if value is None:
            value = 0
        items = self.deserialize(self.fetch(mutagen_file))
        items[self.index] = int(value)
        self.store(mutagen_file, items)

    def delete(self, mutagen_file):
        if self.index == 0:
            super().delete(mutagen_file)
        else:
            self.set(mutagen_file, None)


class MP4ListStorageStyle(ListStorageStyle, MP4StorageStyle):
    pass


class MP4SoundCheckStorageStyle(SoundCheckStorageStyleMixin, MP4StorageStyle):
    def __init__(self, key, index=0, **kwargs):
        super().__init__(key, **kwargs)
        self.index = index


class MP4BoolStorageStyle(MP4StorageStyle):
    """A style for booleans in MPEG-4 files. (MPEG-4 has an atom type
    specifically for representing booleans.)
    """

    def get(self, mutagen_file):
        try:
            return mutagen_file[self.key]
        except KeyError:
            return None

    def get_list(self, mutagen_file):
        raise NotImplementedError("MP4 bool storage does not support lists")

    def set(self, mutagen_file, value):
        mutagen_file[self.key] = value

    def set_list(self, mutagen_file, values):
        raise NotImplementedError("MP4 bool storage does not support lists")


class MP4ImageStorageStyle(MP4ListStorageStyle):
    """Store images as MPEG-4 image atoms. Values are `Image` objects."""

    def __init__(self, **kwargs):
        super().__init__(key="covr", **kwargs)

    def deserialize(self, data):
        return Image(data)

    def serialize(self, image):
        if image.mime_type == "image/png":
            kind = mutagen.mp4.MP4Cover.FORMAT_PNG
        elif image.mime_type == "image/jpeg":
            kind = mutagen.mp4.MP4Cover.FORMAT_JPEG
        else:
            raise ValueError("MP4 files only supports PNG and JPEG images")
        return mutagen.mp4.MP4Cover(image.data, kind)
