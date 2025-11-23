from mediafile.constants import ImageType
from mediafile.utils import Image

from .base import ListStorageStyle


class APEv2ImageStorageStyle(ListStorageStyle):
    """Store images in APEv2 tags. Values are `Image` objects."""

    formats = ["APEv2File", "WavPack", "Musepack", "MonkeysAudio", "OptimFROG"]

    TAG_NAMES = {
        ImageType.other: "Cover Art (other)",
        ImageType.icon: "Cover Art (icon)",
        ImageType.other_icon: "Cover Art (other icon)",
        ImageType.front: "Cover Art (front)",
        ImageType.back: "Cover Art (back)",
        ImageType.leaflet: "Cover Art (leaflet)",
        ImageType.media: "Cover Art (media)",
        ImageType.lead_artist: "Cover Art (lead)",
        ImageType.artist: "Cover Art (artist)",
        ImageType.conductor: "Cover Art (conductor)",
        ImageType.group: "Cover Art (band)",
        ImageType.composer: "Cover Art (composer)",
        ImageType.lyricist: "Cover Art (lyricist)",
        ImageType.recording_location: "Cover Art (studio)",
        ImageType.recording_session: "Cover Art (recording)",
        ImageType.performance: "Cover Art (performance)",
        ImageType.screen_capture: "Cover Art (movie scene)",
        ImageType.fish: "Cover Art (colored fish)",
        ImageType.illustration: "Cover Art (illustration)",
        ImageType.artist_logo: "Cover Art (band logo)",
        ImageType.publisher_logo: "Cover Art (publisher logo)",
    }

    def __init__(self):
        super().__init__(key="")

    def fetch(self, mutagen_file):
        images = []
        for cover_type, cover_tag in self.TAG_NAMES.items():
            try:
                frame = mutagen_file[cover_tag]
                text_delimiter_index = frame.value.find(b"\x00")
                if text_delimiter_index > 0:
                    comment = frame.value[0:text_delimiter_index]
                    comment = comment.decode("utf-8", "replace")
                else:
                    comment = None
                image_data = frame.value[text_delimiter_index + 1 :]
                images.append(Image(data=image_data, type=cover_type, desc=comment))
            except KeyError:
                pass

        return images

    def set_list(self, mutagen_file, values):
        self.delete(mutagen_file)

        for image in values:
            image_type = image.type or ImageType.other
            comment = image.desc or ""
            image_data = comment.encode("utf-8") + b"\x00" + image.data
            cover_tag = self.TAG_NAMES[image_type]
            mutagen_file[cover_tag] = image_data

    def delete(self, mutagen_file):
        """Remove all images from the file."""
        for cover_tag in self.TAG_NAMES.values():
            try:
                del mutagen_file[cover_tag]
            except KeyError:
                pass
