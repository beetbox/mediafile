# This file is part of MediaFile.
# Copyright 2016, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Handles low-level interfacing for files' tags. Wraps Mutagen to
automatically detect file types and provide a unified interface for a
useful subset of music files' tags.

Usage:

    >>> f = MediaFile('Lucy.mp3')
    >>> f.title
    u'Lucy in the Sky with Diamonds'
    >>> f.artist = 'The Beatles'
    >>> f.save()

A field will always return a reasonable value of the correct type, even
if no tag is present. If no value is available, the value will be false
(e.g., zero or the empty string).

Internally ``MediaFile`` uses ``MediaField`` descriptors to access the
data from the tags. In turn ``MediaField`` uses a number of
``StorageStyle`` strategies to handle format specific logic.
"""

import logging
import os
import re

import mutagen
import mutagen.mp3

from .constants import TYPES, ImageType
from .exceptions import FileTypeError, MutagenError, UnreadableFileError
from .fields import (
    CoverArtField,
    DateField,
    DateItemField,
    ImageListField,
    ListMediaField,
    MediaField,
    QNumberField,
)
from .storage import (
    APEv2ImageStorageStyle,
    ASFImageStorageStyle,
    ASFStorageStyle,
    FlacImageStorageStyle,
    ListStorageStyle,
    MP3DescStorageStyle,
    MP3ImageStorageStyle,
    MP3ListDescStorageStyle,
    MP3ListStorageStyle,
    MP3PeopleStorageStyle,
    MP3SlashPackStorageStyle,
    MP3SoundCheckStorageStyle,
    MP3StorageStyle,
    MP3UFIDStorageStyle,
    MP4BoolStorageStyle,
    MP4ImageStorageStyle,
    MP4ListStorageStyle,
    MP4SoundCheckStorageStyle,
    MP4StorageStyle,
    MP4TupleStorageStyle,
    SoundCheckStorageStyleMixin,
    StorageStyle,
    VorbisImageStorageStyle,
)
from .utils import (
    Image,
    image_extension,
    image_mime_type,
    loadfile,
    mutagen_call,
    update_filething,
)

__all__ = [
    "TYPES",
    "APEv2ImageStorageStyle",
    "ASFImageStorageStyle",
    "ASFStorageStyle",
    "CoverArtField",
    "DateField",
    "DateItemField",
    "FileTypeError",
    "FlacImageStorageStyle",
    "Image",
    "ImageListField",
    "ImageType",
    "ListMediaField",
    "ListStorageStyle",
    "MP3DescStorageStyle",
    "MP3ImageStorageStyle",
    "MP3ListDescStorageStyle",
    "MP3ListStorageStyle",
    "MP3PeopleStorageStyle",
    "MP3SlashPackStorageStyle",
    "MP3SoundCheckStorageStyle",
    "MP3StorageStyle",
    "MP3UFIDStorageStyle",
    "MP4BoolStorageStyle",
    "MP4ImageStorageStyle",
    "MP4ListStorageStyle",
    "MP4SoundCheckStorageStyle",
    "MP4StorageStyle",
    "MP4TupleStorageStyle",
    "MediaField",
    "MediaFile",
    "MutagenError",
    "QNumberField",
    "SoundCheckStorageStyleMixin",
    "StorageStyle",
    "UnreadableFileError",
    "VorbisImageStorageStyle",
    "image_extension",
    "image_mime_type",
    "loadfile",
    "mutagen_call",
]

log = logging.getLogger(__name__)


# MediaFile is a collection of fields.


class MediaFile:
    """Represents a multimedia file on disk and provides access to its
    metadata.
    """

    @loadfile()
    def __init__(self, filething, id3v23=False):
        """Constructs a new `MediaFile` reflecting the provided file.

        `filething` can be a path to a file (i.e., a string) or a
        file-like object.

        May throw `UnreadableFileError`.

        By default, MP3 files are saved with ID3v2.4 tags. You can use
        the older ID3v2.3 standard by specifying the `id3v23` option.
        """
        self.filething = filething

        self.mgfile = mutagen_call("open", self.filename, mutagen.File, filething)

        if self.mgfile is None:
            # Mutagen couldn't guess the type
            raise FileTypeError(self.filename)
        elif type(self.mgfile).__name__ in ["M4A", "MP4"]:
            info = self.mgfile.info
            if info.codec and info.codec.startswith("alac"):
                self.type = "alac"
            else:
                self.type = "aac"
        elif type(self.mgfile).__name__ in ["ID3", "MP3"]:
            self.type = "mp3"
        elif type(self.mgfile).__name__ == "FLAC":
            self.type = "flac"
        elif type(self.mgfile).__name__ == "OggOpus":
            self.type = "opus"
        elif type(self.mgfile).__name__ == "OggVorbis":
            self.type = "ogg"
        elif type(self.mgfile).__name__ == "MonkeysAudio":
            self.type = "ape"
        elif type(self.mgfile).__name__ == "WavPack":
            self.type = "wv"
        elif type(self.mgfile).__name__ == "Musepack":
            self.type = "mpc"
        elif type(self.mgfile).__name__ == "ASF":
            self.type = "asf"
        elif type(self.mgfile).__name__ == "AIFF":
            self.type = "aiff"
        elif type(self.mgfile).__name__ == "DSF":
            self.type = "dsf"
        elif type(self.mgfile).__name__ == "WAVE":
            self.type = "wav"
        else:
            raise FileTypeError(self.filename, type(self.mgfile).__name__)

        # Add a set of tags if it's missing.
        if self.mgfile.tags is None:
            self.mgfile.add_tags()

        # Set the ID3v2.3 flag only for MP3s.
        self.id3v23 = id3v23 and self.type == "mp3"

    @property
    def filename(self):
        """The name of the file.

        This is the path if this object was opened from the filesystem,
        or the name of the file-like object.
        """
        return self.filething.name

    @filename.setter
    def filename(self, val):
        """Silently skips setting filename.
        Workaround for `mutagen._util._openfile` setting instance's filename.
        """
        pass

    @property
    def path(self):
        """The path to the file.

        This is `None` if the data comes from a file-like object instead
        of a filesystem path.
        """
        return self.filething.filename

    @property
    def filesize(self):
        """The size (in bytes) of the underlying file."""
        if self.filething.filename:
            return os.path.getsize(self.filething.filename)
        if hasattr(self.filething.fileobj, "__len__"):
            return len(self.filething.fileobj)
        else:
            tell = self.filething.fileobj.tell()
            filesize = self.filething.fileobj.seek(0, 2)
            self.filething.fileobj.seek(tell)
            return filesize

    def save(self, **kwargs):
        """Write the object's tags back to the file.

        May throw `UnreadableFileError`. Accepts keyword arguments to be
        passed to Mutagen's `save` function.
        """
        # Possibly save the tags to ID3v2.3.
        if self.id3v23:
            id3 = self.mgfile
            if hasattr(id3, "tags"):
                # In case this is an MP3 object, not an ID3 object.
                id3 = id3.tags
            id3.update_to_v23()
            kwargs["v2_version"] = 3

        mutagen_call(
            "save",
            self.filename,
            self.mgfile.save,
            update_filething(self.filething),
            **kwargs,
        )

    def delete(self):
        """Remove the current metadata tag from the file. May
        throw `UnreadableFileError`.
        """
        mutagen_call(
            "delete",
            self.filename,
            self.mgfile.delete,
            update_filething(self.filething),
        )

    # Convenient access to the set of available fields.

    @classmethod
    def fields(cls):
        """Get the names of all writable properties that reflect
        metadata tags (i.e., those that are instances of
        :class:`MediaField`).
        """
        for property, descriptor in cls.__dict__.items():
            if isinstance(descriptor, MediaField):
                if isinstance(property, bytes):
                    # On Python 2, class field names are bytes. This method
                    # produces text strings.
                    yield property.decode("utf8", "ignore")
                else:
                    yield property

    @classmethod
    def _field_sort_name(cls, name):
        """Get a sort key for a field name that determines the order
        fields should be written in.

        Fields names are kept unchanged, unless they are instances of
        :class:`DateItemField`, in which case `year`, `month`, and `day`
        are replaced by `date0`, `date1`, and `date2`, respectively, to
        make them appear in that order.
        """
        if isinstance(cls.__dict__[name], DateItemField):
            name = re.sub("year", "date0", name)
            name = re.sub("month", "date1", name)
            name = re.sub("day", "date2", name)
        return name

    @classmethod
    def sorted_fields(cls):
        """Get the names of all writable metadata fields, sorted in the
        order that they should be written.

        This is a lexicographic order, except for instances of
        :class:`DateItemField`, which are sorted in year-month-day
        order.
        """
        yield from sorted(cls.fields(), key=cls._field_sort_name)

    @classmethod
    def readable_fields(cls):
        """Get all metadata fields: the writable ones from
        :meth:`fields` and also other audio properties.
        """
        yield from cls.fields()
        yield from (
            "length",
            "samplerate",
            "bitdepth",
            "bitrate",
            "bitrate_mode",
            "channels",
            "encoder_info",
            "encoder_settings",
            "format",
        )

    @classmethod
    def add_field(cls, name, descriptor):
        """Add a field to store custom tags.

        :param name: the name of the property the field is accessed
                     through. It must not already exist on this class.

        :param descriptor: an instance of :class:`MediaField`.
        """
        if not isinstance(descriptor, MediaField):
            raise ValueError(f"{descriptor} must be an instance of MediaField")
        if name in cls.__dict__:
            raise ValueError(f'property "{name}" already exists on MediaFile')
        setattr(cls, name, descriptor)

    def update(self, dict):
        """Set all field values from a dictionary.

        For any key in `dict` that is also a field to store tags the
        method retrieves the corresponding value from `dict` and updates
        the `MediaFile`. If a key has the value `None`, the
        corresponding property is deleted from the `MediaFile`.
        """
        for field in self.sorted_fields():
            if field in dict:
                if dict[field] is None:
                    delattr(self, field)
                else:
                    setattr(self, field, dict[field])

    def as_dict(self):
        """Get a dictionary with all writable properties that reflect
        metadata tags (i.e., those that are instances of
        :class:`MediaField`).
        """
        return {x: getattr(self, x) for x in self.fields()}

    # Field definitions.

    title = MediaField(
        MP3StorageStyle("TIT2"),
        MP4StorageStyle("\xa9nam"),
        StorageStyle("TITLE"),
        ASFStorageStyle("Title"),
    )
    artist = MediaField(
        MP3StorageStyle("TPE1"),
        MP4StorageStyle("\xa9ART"),
        StorageStyle("ARTIST"),
        ASFStorageStyle("Author"),
    )
    artists = ListMediaField(
        MP3ListDescStorageStyle(desc="ARTISTS"),
        MP4ListStorageStyle("----:com.apple.iTunes:ARTISTS"),
        ListStorageStyle("ARTISTS"),
        ASFStorageStyle("WM/ARTISTS"),
    )
    album = MediaField(
        MP3StorageStyle("TALB"),
        MP4StorageStyle("\xa9alb"),
        StorageStyle("ALBUM"),
        ASFStorageStyle("WM/AlbumTitle"),
    )
    genres = ListMediaField(
        MP3ListStorageStyle("TCON"),
        MP4ListStorageStyle("\xa9gen"),
        ListStorageStyle("GENRE"),
        ASFStorageStyle("WM/Genre"),
    )
    genre = genres.single_field()

    lyricist = MediaField(
        MP3StorageStyle("TEXT"),
        MP4StorageStyle("----:com.apple.iTunes:LYRICIST"),
        StorageStyle("LYRICIST"),
        ASFStorageStyle("WM/Writer"),
    )
    composer = MediaField(
        MP3StorageStyle("TCOM"),
        MP4StorageStyle("\xa9wrt"),
        StorageStyle("COMPOSER"),
        ASFStorageStyle("WM/Composer"),
    )
    composer_sort = MediaField(
        MP3StorageStyle("TSOC"),
        MP4StorageStyle("soco"),
        StorageStyle("COMPOSERSORT"),
        ASFStorageStyle("WM/Composersortorder"),
    )
    arranger = MediaField(
        MP3PeopleStorageStyle("TIPL", involvement="arranger"),
        MP4StorageStyle("----:com.apple.iTunes:Arranger"),
        StorageStyle("ARRANGER"),
        ASFStorageStyle("beets/Arranger"),
    )

    grouping = MediaField(
        MP3StorageStyle("TIT1"),
        MP4StorageStyle("\xa9grp"),
        StorageStyle("GROUPING"),
        ASFStorageStyle("WM/ContentGroupDescription"),
    )
    subtitle = MediaField(
        MP3StorageStyle("TIT3"),
        StorageStyle("SUBTITLE"),
        ASFStorageStyle("Subtitle"),
    )
    track = MediaField(
        MP3SlashPackStorageStyle("TRCK", pack_pos=0),
        MP4TupleStorageStyle("trkn", index=0),
        StorageStyle("TRACK"),
        StorageStyle("TRACKNUMBER"),
        ASFStorageStyle("WM/TrackNumber"),
        out_type=int,
    )
    tracktotal = MediaField(
        MP3SlashPackStorageStyle("TRCK", pack_pos=1),
        MP4TupleStorageStyle("trkn", index=1),
        StorageStyle("TRACKTOTAL"),
        StorageStyle("TRACKC"),
        StorageStyle("TOTALTRACKS"),
        ASFStorageStyle("TotalTracks"),
        out_type=int,
    )
    disc = MediaField(
        MP3SlashPackStorageStyle("TPOS", pack_pos=0),
        MP4TupleStorageStyle("disk", index=0),
        StorageStyle("DISC"),
        StorageStyle("DISCNUMBER"),
        ASFStorageStyle("WM/PartOfSet"),
        out_type=int,
    )
    disctotal = MediaField(
        MP3SlashPackStorageStyle("TPOS", pack_pos=1),
        MP4TupleStorageStyle("disk", index=1),
        StorageStyle("DISCTOTAL"),
        StorageStyle("DISCC"),
        StorageStyle("TOTALDISCS"),
        ASFStorageStyle("TotalDiscs"),
        out_type=int,
    )

    url = MediaField(
        MP3DescStorageStyle(key="WXXX", attr="url", multispec=False),
        MP4StorageStyle("\xa9url"),
        StorageStyle("URL"),
        ASFStorageStyle("WM/URL"),
    )
    lyrics = MediaField(
        MP3DescStorageStyle(key="USLT", multispec=False),
        MP4StorageStyle("\xa9lyr"),
        StorageStyle("LYRICS"),
        ASFStorageStyle("WM/Lyrics"),
    )
    comments = MediaField(
        MP3DescStorageStyle(key="COMM"),
        MP4StorageStyle("\xa9cmt"),
        StorageStyle("DESCRIPTION"),
        StorageStyle("COMMENT"),
        ASFStorageStyle("WM/Comments"),
        ASFStorageStyle("Description"),
    )
    copyright = MediaField(
        MP3StorageStyle("TCOP"),
        MP4StorageStyle("cprt"),
        StorageStyle("COPYRIGHT"),
        ASFStorageStyle("Copyright"),
    )
    bpm = MediaField(
        MP3StorageStyle("TBPM"),
        MP4StorageStyle("tmpo", as_type=int),
        StorageStyle("BPM"),
        ASFStorageStyle("WM/BeatsPerMinute"),
        out_type=int,
    )
    comp = MediaField(
        MP3StorageStyle("TCMP"),
        MP4BoolStorageStyle("cpil"),
        StorageStyle("COMPILATION"),
        ASFStorageStyle("WM/IsCompilation", as_type=bool),
        out_type=bool,
    )
    albumartist = MediaField(
        MP3StorageStyle("TPE2"),
        MP4StorageStyle("aART"),
        StorageStyle("ALBUM ARTIST"),
        StorageStyle("ALBUM_ARTIST"),
        StorageStyle("ALBUMARTIST"),
        ASFStorageStyle("WM/AlbumArtist"),
    )
    albumartists = ListMediaField(
        MP3ListDescStorageStyle(desc="ALBUMARTISTS"),
        MP3ListDescStorageStyle(desc="ALBUM_ARTISTS"),
        MP3ListDescStorageStyle(desc="ALBUM ARTISTS", read_only=True),
        MP4ListStorageStyle("----:com.apple.iTunes:ALBUMARTISTS"),
        MP4ListStorageStyle("----:com.apple.iTunes:ALBUM_ARTISTS"),
        MP4ListStorageStyle("----:com.apple.iTunes:ALBUM ARTISTS", read_only=True),
        ListStorageStyle("ALBUMARTISTS"),
        ListStorageStyle("ALBUM_ARTISTS"),
        ListStorageStyle("ALBUM ARTISTS", read_only=True),
        ASFStorageStyle("WM/AlbumArtists"),
    )
    albumtypes = ListMediaField(
        MP3ListDescStorageStyle("MusicBrainz Album Type", split_v23=True),
        MP4ListStorageStyle("----:com.apple.iTunes:MusicBrainz Album Type"),
        ListStorageStyle("RELEASETYPE"),
        ListStorageStyle("MUSICBRAINZ_ALBUMTYPE"),
        ASFStorageStyle("MusicBrainz/Album Type"),
    )
    albumtype = albumtypes.single_field()

    label = MediaField(
        MP3StorageStyle("TPUB"),
        MP3DescStorageStyle("LABEL"),
        MP4StorageStyle("----:com.apple.iTunes:LABEL"),
        MP4StorageStyle("----:com.apple.iTunes:publisher"),
        MP4StorageStyle("----:com.apple.iTunes:Label", read_only=True),
        StorageStyle("LABEL"),
        StorageStyle("PUBLISHER"),  # Traktor
        ASFStorageStyle("WM/Publisher"),
    )
    artist_sort = MediaField(
        MP3StorageStyle("TSOP"),
        MP4StorageStyle("soar"),
        StorageStyle("ARTISTSORT"),
        ASFStorageStyle("WM/ArtistSortOrder"),
    )
    albumartist_sort = MediaField(
        MP3StorageStyle("TSO2"),
        MP3DescStorageStyle("ALBUMARTISTSORT"),
        MP4StorageStyle("soaa"),
        StorageStyle("ALBUMARTISTSORT"),
        ASFStorageStyle("WM/AlbumArtistSortOrder"),
    )
    asin = MediaField(
        MP3DescStorageStyle("ASIN"),
        MP4StorageStyle("----:com.apple.iTunes:ASIN"),
        StorageStyle("ASIN"),
        ASFStorageStyle("MusicBrainz/ASIN"),
    )
    catalognums = ListMediaField(
        MP3ListDescStorageStyle("CATALOGNUMBER", split_v23=True),
        MP3ListDescStorageStyle("CATALOGID", read_only=True),
        MP3ListDescStorageStyle("DISCOGS_CATALOG", read_only=True),
        MP4ListStorageStyle("----:com.apple.iTunes:CATALOGNUMBER"),
        MP4ListStorageStyle("----:com.apple.iTunes:CATALOGID", read_only=True),
        MP4ListStorageStyle("----:com.apple.iTunes:DISCOGS_CATALOG", read_only=True),
        ListStorageStyle("CATALOGNUMBER"),
        ListStorageStyle("CATALOGID", read_only=True),
        ListStorageStyle("DISCOGS_CATALOG", read_only=True),
        ASFStorageStyle("WM/CatalogNo"),
        ASFStorageStyle("CATALOGID", read_only=True),
        ASFStorageStyle("DISCOGS_CATALOG", read_only=True),
    )
    catalognum = catalognums.single_field()

    barcode = MediaField(
        MP3DescStorageStyle("BARCODE"),
        MP4StorageStyle("----:com.apple.iTunes:BARCODE"),
        StorageStyle("BARCODE"),
        StorageStyle("UPC", read_only=True),
        StorageStyle("EAN/UPN", read_only=True),
        StorageStyle("EAN", read_only=True),
        StorageStyle("UPN", read_only=True),
        ASFStorageStyle("WM/Barcode"),
    )
    isrc = MediaField(
        MP3StorageStyle("TSRC"),
        MP4StorageStyle("----:com.apple.iTunes:ISRC"),
        StorageStyle("ISRC"),
        ASFStorageStyle("WM/ISRC"),
    )
    disctitle = MediaField(
        MP3StorageStyle("TSST"),
        MP4StorageStyle("----:com.apple.iTunes:DISCSUBTITLE"),
        StorageStyle("DISCSUBTITLE"),
        ASFStorageStyle("WM/SetSubTitle"),
    )
    encoder = MediaField(
        MP3StorageStyle("TENC"),
        MP4StorageStyle("\xa9too"),
        StorageStyle("ENCODEDBY"),
        StorageStyle("ENCODER"),
        ASFStorageStyle("WM/EncodedBy"),
    )
    script = MediaField(
        MP3DescStorageStyle("Script"),
        MP4StorageStyle("----:com.apple.iTunes:SCRIPT"),
        StorageStyle("SCRIPT"),
        ASFStorageStyle("WM/Script"),
    )
    languages = ListMediaField(
        MP3ListStorageStyle("TLAN"),
        MP4ListStorageStyle("----:com.apple.iTunes:LANGUAGE"),
        ListStorageStyle("LANGUAGE"),
        ASFStorageStyle("WM/Language"),
    )
    language = languages.single_field()

    country = MediaField(
        MP3DescStorageStyle("MusicBrainz Album Release Country"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Album Release Country"),
        StorageStyle("RELEASECOUNTRY"),
        ASFStorageStyle("MusicBrainz/Album Release Country"),
    )
    albumstatus = MediaField(
        MP3DescStorageStyle("MusicBrainz Album Status"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Album Status"),
        StorageStyle("RELEASESTATUS"),
        StorageStyle("MUSICBRAINZ_ALBUMSTATUS"),
        ASFStorageStyle("MusicBrainz/Album Status"),
    )
    media = MediaField(
        MP3StorageStyle("TMED"),
        MP3DescStorageStyle("MEDIA"),
        MP4StorageStyle("----:com.apple.iTunes:MEDIA"),
        StorageStyle("MEDIA"),
        ASFStorageStyle("WM/Media"),
    )
    albumdisambig = MediaField(
        # This tag mapping was invented for beets (not used by Picard, etc).
        MP3DescStorageStyle("MusicBrainz Album Comment"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Album Comment"),
        StorageStyle("MUSICBRAINZ_ALBUMCOMMENT"),
        ASFStorageStyle("MusicBrainz/Album Comment"),
    )

    # Release date.
    date = DateField(
        MP3StorageStyle("TDRC"),
        MP4StorageStyle("\xa9day"),
        StorageStyle("DATE"),
        ASFStorageStyle("WM/Year"),
        year=(StorageStyle("YEAR"),),
    )

    year = date.year_field()
    month = date.month_field()
    day = date.day_field()

    # *Original* release date.
    original_date = DateField(
        MP3StorageStyle("TDOR"),
        MP4StorageStyle("----:com.apple.iTunes:ORIGINAL YEAR"),
        MP4StorageStyle("----:com.apple.iTunes:ORIGINALDATE"),
        StorageStyle("ORIGINALDATE"),
        ASFStorageStyle("WM/OriginalReleaseYear"),
    )

    original_year = original_date.year_field()
    original_month = original_date.month_field()
    original_day = original_date.day_field()

    # Nonstandard metadata.
    artist_credit = MediaField(
        MP3DescStorageStyle("Artist Credit"),
        MP4StorageStyle("----:com.apple.iTunes:Artist Credit"),
        StorageStyle("ARTIST_CREDIT"),
        ASFStorageStyle("beets/Artist Credit"),
    )
    artists_credit = ListMediaField(
        MP3ListDescStorageStyle(desc="ARTISTS_CREDIT"),
        MP4ListStorageStyle("----:com.apple.iTunes:ARTISTS_CREDIT"),
        ListStorageStyle("ARTISTS_CREDIT"),
        ASFStorageStyle("beets/ArtistsCredit"),
    )
    artists_sort = ListMediaField(
        MP3ListDescStorageStyle(desc="ARTISTS_SORT"),
        MP4ListStorageStyle("----:com.apple.iTunes:ARTISTS_SORT"),
        ListStorageStyle("ARTISTS_SORT"),
        ASFStorageStyle("beets/ArtistsSort"),
    )
    albumartist_credit = MediaField(
        MP3DescStorageStyle("Album Artist Credit"),
        MP4StorageStyle("----:com.apple.iTunes:Album Artist Credit"),
        StorageStyle("ALBUMARTIST_CREDIT"),
        ASFStorageStyle("beets/Album Artist Credit"),
    )
    albumartists_credit = ListMediaField(
        MP3ListDescStorageStyle(desc="ALBUMARTISTS_CREDIT"),
        MP4ListStorageStyle("----:com.apple.iTunes:ALBUMARTISTS_CREDIT"),
        ListStorageStyle("ALBUMARTISTS_CREDIT"),
        ASFStorageStyle("beets/AlbumArtistsCredit"),
    )
    albumartists_sort = ListMediaField(
        MP3ListDescStorageStyle(desc="ALBUMARTISTS_SORT"),
        MP4ListStorageStyle("----:com.apple.iTunes:ALBUMARTISTS_SORT"),
        ListStorageStyle("ALBUMARTISTS_SORT"),
        ASFStorageStyle("beets/AlbumArtistsSort"),
    )

    # Legacy album art field
    art = CoverArtField()

    # Image list
    images = ImageListField()

    # MusicBrainz IDs.
    mb_trackid = MediaField(
        MP3UFIDStorageStyle(owner="http://musicbrainz.org"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Track Id"),
        StorageStyle("MUSICBRAINZ_TRACKID"),
        ASFStorageStyle("MusicBrainz/Track Id"),
    )
    mb_releasetrackid = MediaField(
        MP3DescStorageStyle("MusicBrainz Release Track Id"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Release Track Id"),
        StorageStyle("MUSICBRAINZ_RELEASETRACKID"),
        ASFStorageStyle("MusicBrainz/Release Track Id"),
    )
    mb_workid = MediaField(
        MP3DescStorageStyle("MusicBrainz Work Id"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Work Id"),
        StorageStyle("MUSICBRAINZ_WORKID"),
        ASFStorageStyle("MusicBrainz/Work Id"),
    )
    mb_albumid = MediaField(
        MP3DescStorageStyle("MusicBrainz Album Id"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Album Id"),
        StorageStyle("MUSICBRAINZ_ALBUMID"),
        ASFStorageStyle("MusicBrainz/Album Id"),
    )
    mb_artistids = ListMediaField(
        MP3ListDescStorageStyle("MusicBrainz Artist Id", split_v23=True),
        MP4ListStorageStyle("----:com.apple.iTunes:MusicBrainz Artist Id"),
        ListStorageStyle("MUSICBRAINZ_ARTISTID"),
        ASFStorageStyle("MusicBrainz/Artist Id"),
    )
    mb_artistid = mb_artistids.single_field()

    mb_albumartistids = ListMediaField(
        MP3ListDescStorageStyle(
            "MusicBrainz Album Artist Id",
            split_v23=True,
        ),
        MP4ListStorageStyle(
            "----:com.apple.iTunes:MusicBrainz Album Artist Id",
        ),
        ListStorageStyle("MUSICBRAINZ_ALBUMARTISTID"),
        ASFStorageStyle("MusicBrainz/Album Artist Id"),
    )
    mb_albumartistid = mb_albumartistids.single_field()

    mb_releasegroupid = MediaField(
        MP3DescStorageStyle("MusicBrainz Release Group Id"),
        MP4StorageStyle("----:com.apple.iTunes:MusicBrainz Release Group Id"),
        StorageStyle("MUSICBRAINZ_RELEASEGROUPID"),
        ASFStorageStyle("MusicBrainz/Release Group Id"),
    )

    # Acoustid fields.
    acoustid_fingerprint = MediaField(
        MP3DescStorageStyle("Acoustid Fingerprint"),
        MP4StorageStyle("----:com.apple.iTunes:Acoustid Fingerprint"),
        StorageStyle("ACOUSTID_FINGERPRINT"),
        ASFStorageStyle("Acoustid/Fingerprint"),
    )
    acoustid_id = MediaField(
        MP3DescStorageStyle("Acoustid Id"),
        MP4StorageStyle("----:com.apple.iTunes:Acoustid Id"),
        StorageStyle("ACOUSTID_ID"),
        ASFStorageStyle("Acoustid/Id"),
    )

    # ReplayGain fields.
    rg_track_gain = MediaField(
        MP3DescStorageStyle("REPLAYGAIN_TRACK_GAIN", float_places=2, suffix=" dB"),
        MP3DescStorageStyle("replaygain_track_gain", float_places=2, suffix=" dB"),
        MP3SoundCheckStorageStyle(key="COMM", index=0, desc="iTunNORM", id3_lang="eng"),
        MP4StorageStyle(
            "----:com.apple.iTunes:replaygain_track_gain", float_places=2, suffix=" dB"
        ),
        MP4SoundCheckStorageStyle("----:com.apple.iTunes:iTunNORM", index=0),
        StorageStyle("REPLAYGAIN_TRACK_GAIN", float_places=2, suffix=" dB"),
        ASFStorageStyle("replaygain_track_gain", float_places=2, suffix=" dB"),
        out_type=float,
    )
    rg_album_gain = MediaField(
        MP3DescStorageStyle("REPLAYGAIN_ALBUM_GAIN", float_places=2, suffix=" dB"),
        MP3DescStorageStyle("replaygain_album_gain", float_places=2, suffix=" dB"),
        MP4StorageStyle(
            "----:com.apple.iTunes:replaygain_album_gain", float_places=2, suffix=" dB"
        ),
        StorageStyle("REPLAYGAIN_ALBUM_GAIN", float_places=2, suffix=" dB"),
        ASFStorageStyle("replaygain_album_gain", float_places=2, suffix=" dB"),
        out_type=float,
    )
    rg_track_peak = MediaField(
        MP3DescStorageStyle("REPLAYGAIN_TRACK_PEAK", float_places=6),
        MP3DescStorageStyle("replaygain_track_peak", float_places=6),
        MP3SoundCheckStorageStyle(key="COMM", index=1, desc="iTunNORM", id3_lang="eng"),
        MP4StorageStyle("----:com.apple.iTunes:replaygain_track_peak", float_places=6),
        MP4SoundCheckStorageStyle("----:com.apple.iTunes:iTunNORM", index=1),
        StorageStyle("REPLAYGAIN_TRACK_PEAK", float_places=6),
        ASFStorageStyle("replaygain_track_peak", float_places=6),
        out_type=float,
    )
    rg_album_peak = MediaField(
        MP3DescStorageStyle("REPLAYGAIN_ALBUM_PEAK", float_places=6),
        MP3DescStorageStyle("replaygain_album_peak", float_places=6),
        MP4StorageStyle("----:com.apple.iTunes:replaygain_album_peak", float_places=6),
        StorageStyle("REPLAYGAIN_ALBUM_PEAK", float_places=6),
        ASFStorageStyle("replaygain_album_peak", float_places=6),
        out_type=float,
    )

    # EBU R128 fields.
    r128_track_gain = QNumberField(
        8,
        MP3DescStorageStyle("R128_TRACK_GAIN"),
        MP4StorageStyle("----:com.apple.iTunes:R128_TRACK_GAIN"),
        StorageStyle("R128_TRACK_GAIN"),
        ASFStorageStyle("R128_TRACK_GAIN"),
    )
    r128_album_gain = QNumberField(
        8,
        MP3DescStorageStyle("R128_ALBUM_GAIN"),
        MP4StorageStyle("----:com.apple.iTunes:R128_ALBUM_GAIN"),
        StorageStyle("R128_ALBUM_GAIN"),
        ASFStorageStyle("R128_ALBUM_GAIN"),
    )

    initial_key = MediaField(
        MP3StorageStyle("TKEY"),
        MP4StorageStyle("----:com.apple.iTunes:initialkey"),
        StorageStyle("INITIALKEY"),
        ASFStorageStyle("INITIALKEY"),
    )

    @property
    def length(self):
        """The duration of the audio in seconds (a float)."""
        return self.mgfile.info.length

    @property
    def samplerate(self):
        """The audio's sample rate (an int)."""
        if hasattr(self.mgfile.info, "sample_rate"):
            return self.mgfile.info.sample_rate
        elif self.type == "opus":
            # Opus is always 48kHz internally.
            return 48000
        return 0

    @property
    def bitdepth(self):
        """The number of bits per sample in the audio encoding (an int).
        Only available for certain file formats (zero where
        unavailable).
        """
        if hasattr(self.mgfile.info, "bits_per_sample"):
            return self.mgfile.info.bits_per_sample
        return 0

    @property
    def channels(self):
        """The number of channels in the audio (an int)."""
        if hasattr(self.mgfile.info, "channels"):
            return self.mgfile.info.channels
        return 0

    @property
    def bitrate(self):
        """The number of bits per seconds used in the audio coding (an
        int). If this is provided explicitly by the compressed file
        format, this is a precise reflection of the encoding. Otherwise,
        it is estimated from the on-disk file size. In this case, some
        imprecision is possible because the file header is incorporated
        in the file size.
        """
        if hasattr(self.mgfile.info, "bitrate") and self.mgfile.info.bitrate:
            # Many formats provide it explicitly.
            return self.mgfile.info.bitrate
        else:
            # Otherwise, we calculate bitrate from the file size. (This
            # is the case for all of the lossless formats.)
            if not self.length:
                # Avoid division by zero if length is not available.
                return 0
            return int(self.filesize * 8 / self.length)

    @property
    def bitrate_mode(self):
        """The mode of the bitrate used in the audio coding
        (a string, eg. "CBR", "VBR" or "ABR").
        Only available for the MP3 file format (empty where unavailable).
        """
        if hasattr(self.mgfile.info, "bitrate_mode"):
            return {
                mutagen.mp3.BitrateMode.CBR: "CBR",
                mutagen.mp3.BitrateMode.VBR: "VBR",
                mutagen.mp3.BitrateMode.ABR: "ABR",
            }.get(self.mgfile.info.bitrate_mode, "")
        else:
            return ""

    @property
    def encoder_info(self):
        """The name and/or version of the encoder used
        (a string, eg. "LAME 3.97.0").
        Only available for some formats (empty where unavailable).
        """
        if hasattr(self.mgfile.info, "encoder_info"):
            return self.mgfile.info.encoder_info
        else:
            return ""

    @property
    def encoder_settings(self):
        """A guess of the settings used for the encoder (a string, eg. "-V2").
        Only available for the MP3 file format (empty where unavailable).
        """
        if hasattr(self.mgfile.info, "encoder_settings"):
            return self.mgfile.info.encoder_settings
        else:
            return ""

    @property
    def format(self):
        """A string describing the file format/codec."""
        return TYPES[self.type]
