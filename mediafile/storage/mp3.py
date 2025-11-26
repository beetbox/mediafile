import mutagen
import mutagen.id3

from mediafile.utils import Image

from .base import ListStorageStyle, SoundCheckStorageStyleMixin, StorageStyle


class MP3StorageStyle(StorageStyle):
    """Store data in ID3 frames."""

    formats = ["MP3", "AIFF", "DSF", "WAVE"]

    def __init__(self, key, id3_lang=None, **kwargs):
        """Create a new ID3 storage style. `id3_lang` is the value for
        the language field of newly created frames.
        """
        self.id3_lang = id3_lang
        super().__init__(key, **kwargs)

    def fetch(self, mutagen_file):
        try:
            return mutagen_file[self.key].text[0]
        except (KeyError, IndexError):
            return None

    def store(self, mutagen_file, value):
        frame = mutagen.id3.Frames[self.key](encoding=3, text=[value])
        mutagen_file.tags.setall(self.key, [frame])


class MP3PeopleStorageStyle(MP3StorageStyle):
    """Store list of people in ID3 frames."""

    def __init__(self, key, involvement="", **kwargs):
        self.involvement = involvement
        super().__init__(key, **kwargs)

    def store(self, mutagen_file, value):
        frames = mutagen_file.tags.getall(self.key)

        # Try modifying in place.
        found = False
        for frame in frames:
            if frame.encoding == mutagen.id3._specs.Encoding.UTF8:
                for pair in frame.people:
                    if pair[0].lower() == self.involvement.lower():
                        pair[1] = value
                        found = True

        # Try creating a new frame.
        if not found:
            frame = mutagen.id3.Frames[self.key](
                encoding=mutagen.id3._specs.Encoding.UTF8,
                people=[[self.involvement, value]],
            )
            mutagen_file.tags.add(frame)

    def fetch(self, mutagen_file):
        for frame in mutagen_file.tags.getall(self.key):
            for pair in frame.people:
                if pair[0].lower() == self.involvement.lower():
                    try:
                        return pair[1]
                    except IndexError:
                        return None


class MP3ListStorageStyle(ListStorageStyle, MP3StorageStyle):
    """Store lists of data in multiple ID3 frames."""

    def fetch(self, mutagen_file):
        try:
            return mutagen_file[self.key].text
        except KeyError:
            return []

    def store(self, mutagen_file, values):
        frame = mutagen.id3.Frames[self.key](encoding=3, text=values)
        mutagen_file.tags.setall(self.key, [frame])


class MP3UFIDStorageStyle(MP3StorageStyle):
    """Store string data in a UFID ID3 frame with a particular owner."""

    def __init__(self, owner, **kwargs):
        self.owner = owner
        super().__init__("UFID:" + owner, **kwargs)

    def fetch(self, mutagen_file):
        try:
            return mutagen_file[self.key].data
        except KeyError:
            return None

    def store(self, mutagen_file, value):
        # This field type stores text data as encoded data.
        assert isinstance(value, str)
        value = value.encode("utf-8")

        frames = mutagen_file.tags.getall(self.key)
        for frame in frames:
            # Replace existing frame data.
            if frame.owner == self.owner:
                frame.data = value
        else:
            # New frame.
            frame = mutagen.id3._frames.UFID(owner=self.owner, data=value)
            mutagen_file.tags.setall(self.key, [frame])


class MP3DescStorageStyle(MP3StorageStyle):
    """Store data in a TXXX (or similar) ID3 frame. The frame is
    selected based its ``desc`` field.
    ``attr`` allows to specify name of data accessor property in the frame.
    Most of frames use `text`.
    ``multispec`` specifies if frame data is ``mutagen.id3.MultiSpec``
    which means that the data is being packed in the list.
    """

    def __init__(self, desc="", key="TXXX", attr="text", multispec=True, **kwargs):
        assert isinstance(desc, str)
        self.description = desc
        self.attr = attr
        self.multispec = multispec
        super().__init__(key=key, **kwargs)

    def store(self, mutagen_file, value):
        frames = mutagen_file.tags.getall(self.key)
        if self.multispec:
            value = [value]

        # Try modifying in place.
        found = False
        for frame in frames:
            if frame.desc.lower() == self.description.lower():
                setattr(frame, self.attr, value)
                frame.encoding = mutagen.id3._specs.Encoding.UTF8
                found = True

        # Try creating a new frame.
        if not found:
            frame = mutagen.id3.Frames[self.key](
                desc=self.description,
                encoding=mutagen.id3._specs.Encoding.UTF8,
                **{self.attr: value},
            )
            if self.id3_lang:
                frame.lang = self.id3_lang
            mutagen_file.tags.add(frame)

    def fetch(self, mutagen_file):
        for frame in mutagen_file.tags.getall(self.key):
            if frame.desc.lower() == self.description.lower():
                if not self.multispec:
                    return getattr(frame, self.attr)
                try:
                    return getattr(frame, self.attr)[0]
                except IndexError:
                    return None

    def delete(self, mutagen_file):
        found_frame = None
        for frame in mutagen_file.tags.getall(self.key):
            if frame.desc.lower() == self.description.lower():
                found_frame = frame
                break
        if found_frame is not None:
            del mutagen_file[frame.HashKey]


class MP3ListDescStorageStyle(MP3DescStorageStyle, ListStorageStyle):
    def __init__(self, desc="", key="TXXX", split_v23=False, **kwargs):
        self.split_v23 = split_v23
        super().__init__(desc=desc, key=key, **kwargs)

    def fetch(self, mutagen_file):
        for frame in mutagen_file.tags.getall(self.key):
            if frame.desc.lower() == self.description.lower():
                if mutagen_file.tags.version == (2, 3, 0) and self.split_v23:
                    return sum((el.split("/") for el in frame.text), [])
                else:
                    return frame.text
        return []

    def store(self, mutagen_file, values):
        self.delete(mutagen_file)
        frame = mutagen.id3.Frames[self.key](
            desc=self.description,
            text=values,
            encoding=mutagen.id3._specs.Encoding.UTF8,
        )
        if self.id3_lang:
            frame.lang = self.id3_lang
        mutagen_file.tags.add(frame)


class MP3SlashPackStorageStyle(MP3StorageStyle):
    """Store value as part of pair that is serialized as a slash-
    separated string.
    """

    def __init__(self, key, pack_pos=0, **kwargs):
        super().__init__(key, **kwargs)
        self.pack_pos = pack_pos

    def _fetch_unpacked(self, mutagen_file):
        data = self.fetch(mutagen_file)
        if data:
            items = str(data).split("/")
        else:
            items = []
        packing_length = 2
        return list(items) + [None] * (packing_length - len(items))

    def get(self, mutagen_file):
        return self._fetch_unpacked(mutagen_file)[self.pack_pos]

    def set(self, mutagen_file, value):
        items = self._fetch_unpacked(mutagen_file)
        items[self.pack_pos] = value
        if items[0] is None:
            items[0] = ""
        if items[1] is None:
            items.pop()  # Do not store last value
        self.store(mutagen_file, "/".join(map(str, items)))

    def delete(self, mutagen_file):
        if self.pack_pos == 0:
            super().delete(mutagen_file)
        else:
            self.set(mutagen_file, None)


class MP3ImageStorageStyle(ListStorageStyle, MP3StorageStyle):
    """Converts between APIC frames and ``Image`` instances.

    The `get_list` method inherited from ``ListStorageStyle`` returns a
    list of ``Image``s. Similarly, the `set_list` method accepts a
    list of ``Image``s as its ``values`` argument.
    """

    def __init__(self):
        super().__init__(key="APIC")
        self.as_type = bytes

    def deserialize(self, apic_frame):
        """Convert APIC frame into Image."""
        return Image(data=apic_frame.data, desc=apic_frame.desc, type=apic_frame.type)

    def fetch(self, mutagen_file):
        return mutagen_file.tags.getall(self.key)

    def store(self, mutagen_file, frames):
        mutagen_file.tags.setall(self.key, frames)

    def delete(self, mutagen_file):
        mutagen_file.tags.delall(self.key)

    def serialize(self, image):
        """Return an APIC frame populated with data from ``image``."""
        assert isinstance(image, Image)
        frame = mutagen.id3.Frames[self.key]()
        frame.data = image.data
        frame.mime = image.mime_type
        frame.desc = image.desc or ""

        # For compatibility with OS X/iTunes prefer latin-1 if possible.
        # See issue #899
        try:
            frame.desc.encode("latin-1")
        except UnicodeEncodeError:
            frame.encoding = mutagen.id3._specs.Encoding.UTF16
        else:
            frame.encoding = mutagen.id3._specs.Encoding.LATIN1

        frame.type = image.type_index
        return frame


class MP3SoundCheckStorageStyle(SoundCheckStorageStyleMixin, MP3DescStorageStyle):
    def __init__(self, index=0, **kwargs):
        super().__init__(**kwargs)
        self.index = index
