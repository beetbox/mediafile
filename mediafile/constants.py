import enum

# Human-readable type names.
TYPES = {
    "mp3": "MP3",
    "aac": "AAC",
    "alac": "ALAC",
    "ogg": "OGG",
    "opus": "Opus",
    "flac": "FLAC",
    "ape": "APE",
    "wv": "WavPack",
    "mpc": "Musepack",
    "asf": "Windows Media",
    "aiff": "AIFF",
    "dsf": "DSD Stream File",
    "wav": "WAVE",
}


class ImageType(enum.Enum):
    """Indicates the kind of an `Image` stored in a file's tag."""

    other = 0
    icon = 1
    other_icon = 2
    front = 3
    back = 4
    leaflet = 5
    media = 6
    lead_artist = 7
    artist = 8
    conductor = 9
    group = 10
    composer = 11
    lyricist = 12
    recording_location = 13
    recording_session = 14
    performance = 15
    screen_capture = 16
    fish = 17
    illustration = 18
    artist_logo = 19
    publisher_logo = 20
