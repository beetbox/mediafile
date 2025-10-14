from .afs import ASFImageStorageStyle, ASFStorageStyle
from .ape import APEv2ImageStorageStyle
from .flac import FlacImageStorageStyle
from .mp3 import MP3ImageStorageStyle, MP3PeopleStorageStyle, MP3StorageStyle
from .mp4 import MP4ImageStorageStyle, MP4SoundCheckStorageStyle, MP4StorageStyle
from .vorbis import VorbisImageStorageStyle

__all__ = [
    "ASFStorageStyle",
    "ASFImageStorageStyle",
    "APEv2ImageStorageStyle",
    "FlacImageStorageStyle",
    "MP3StorageStyle",
    "MP3PeopleStorageStyle",
    "MP3ImageStorageStyle",
    "MP4StorageStyle",
    "MP4SoundCheckStorageStyle",
    "MP4ImageStorageStyle",
    "VorbisImageStorageStyle",
]
