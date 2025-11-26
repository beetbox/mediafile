# MediaField is a descriptor that represents a single logical field. It
# aggregates several StorageStyles describing how to access the data for
# each file type.
import datetime
import re

from mediafile.utils import Image, safe_cast

from .constants import ImageType
from .storage import (
    APEv2ImageStorageStyle,
    ASFImageStorageStyle,
    FlacImageStorageStyle,
    MP3ImageStorageStyle,
    MP4ImageStorageStyle,
    VorbisImageStorageStyle,
)


class MediaField:
    """A descriptor providing access to a particular (abstract) metadata
    field.
    """

    def __init__(self, *styles, **kwargs):
        """Creates a new MediaField.

        :param styles: `StorageStyle` instances that describe the strategy
                       for reading and writing the field in particular
                       formats. There must be at least one style for
                       each possible file format.

        :param out_type: the type of the value that should be returned when
                         getting this property.

        """
        self.out_type = kwargs.get("out_type", str)
        self._styles = styles

    def styles(self, mutagen_file):
        """Yields the list of storage styles of this field that can
        handle the MediaFile's format.
        """
        for style in self._styles:
            if mutagen_file.__class__.__name__ in style.formats:
                yield style

    def __get__(self, mediafile, owner=None):
        out = None
        for style in self.styles(mediafile.mgfile):
            out = style.get(mediafile.mgfile)
            if out:
                break
        return safe_cast(self.out_type, out)

    def __set__(self, mediafile, value):
        if value is None:
            value = self._none_value()
        for style in self.styles(mediafile.mgfile):
            if not style.read_only:
                style.set(mediafile.mgfile, value)

    def __delete__(self, mediafile):
        for style in self.styles(mediafile.mgfile):
            style.delete(mediafile.mgfile)

    def _none_value(self):
        """Get an appropriate "null" value for this field's type. This
        is used internally when setting the field to None.
        """
        if self.out_type is int:
            return 0
        elif self.out_type is float:
            return 0.0
        elif self.out_type is bool:
            return False
        elif self.out_type is str:
            return ""


class ListMediaField(MediaField):
    """Property descriptor that retrieves a list of multiple values from
    a tag.

    Uses ``get_list`` and set_list`` methods of its ``StorageStyle``
    strategies to do the actual work.
    """

    def __get__(self, mediafile, _=None):
        for style in self.styles(mediafile.mgfile):
            values = style.get_list(mediafile.mgfile)
            if values:
                return [safe_cast(self.out_type, value) for value in values]
        return None

    def __set__(self, mediafile, values):
        for style in self.styles(mediafile.mgfile):
            if not style.read_only:
                style.set_list(mediafile.mgfile, values)

    def single_field(self):
        """Returns a ``MediaField`` descriptor that gets and sets the
        first item.
        """
        options = {"out_type": self.out_type}
        return MediaField(*self._styles, **options)


class DateField(MediaField):
    """Descriptor that handles serializing and deserializing dates

    The getter parses value from tags into a ``datetime.date`` instance
    and setter serializes such an instance into a string.

    For granular access to year, month, and day, use the ``*_field``
    methods to create corresponding `DateItemField`s.
    """

    def __init__(self, *date_styles, **kwargs):
        """``date_styles`` is a list of ``StorageStyle``s to store and
        retrieve the whole date from. The ``year`` option is an
        additional list of fallback styles for the year. The year is
        always set on this style, but is only retrieved if the main
        storage styles do not return a value.
        """
        super().__init__(*date_styles)
        year_style = kwargs.get("year", None)
        if year_style:
            self._year_field = MediaField(*year_style)

    def __get__(self, mediafile, owner=None):
        year, month, day = self._get_date_tuple(mediafile)
        if not year:
            return None
        try:
            return datetime.date(year, month or 1, day or 1)
        except ValueError:  # Out of range values.
            return None

    def __set__(self, mediafile, date):
        if date is None:
            self._set_date_tuple(mediafile, None, None, None)
        else:
            self._set_date_tuple(mediafile, date.year, date.month, date.day)

    def __delete__(self, mediafile):
        super().__delete__(mediafile)
        if hasattr(self, "_year_field"):
            self._year_field.__delete__(mediafile)

    def _get_date_tuple(self, mediafile):
        """Get a 3-item sequence representing the date consisting of a
        year, month, and day number. Each number is either an integer or
        None.
        """
        # Get the underlying data and split on hyphens and slashes.
        datestring = super().__get__(mediafile, None)
        if isinstance(datestring, str):
            datestring = re.sub(r"[Tt ].*$", "", str(datestring))
            items = re.split("[-/]", str(datestring))
        else:
            items = []

        # Ensure that we have exactly 3 components, possibly by
        # truncating or padding.
        items = items[:3]
        if len(items) < 3:
            items += [None] * (3 - len(items))

        # Use year field if year is missing.
        if not items[0] and hasattr(self, "_year_field"):
            items[0] = self._year_field.__get__(mediafile)

        # Convert each component to an integer if possible.
        items_ = []
        for item in items:
            try:
                items_.append(int(item))
            except (TypeError, ValueError):
                items_.append(None)
        return items_

    def _set_date_tuple(self, mediafile, year, month=None, day=None):
        """Set the value of the field given a year, month, and day
        number. Each number can be an integer or None to indicate an
        unset component.
        """
        if year is None:
            self.__delete__(mediafile)
            return

        date = [f"{int(year):04d}"]
        if month:
            date.append(f"{int(month):02d}")
        if month and day:
            date.append(f"{int(day):02d}")
        date = map(str, date)
        super().__set__(mediafile, "-".join(date))

        if hasattr(self, "_year_field"):
            self._year_field.__set__(mediafile, year)

    def year_field(self):
        return DateItemField(self, 0)

    def month_field(self):
        return DateItemField(self, 1)

    def day_field(self):
        return DateItemField(self, 2)


class DateItemField(MediaField):
    """Descriptor that gets and sets constituent parts of a `DateField`:
    the month, day, or year.
    """

    def __init__(self, date_field, item_pos):
        self.date_field = date_field
        self.item_pos = item_pos

    def __get__(self, mediafile, _):
        return self.date_field._get_date_tuple(mediafile)[self.item_pos]

    def __set__(self, mediafile, value):
        items = self.date_field._get_date_tuple(mediafile)
        items[self.item_pos] = value
        self.date_field._set_date_tuple(mediafile, *items)

    def __delete__(self, mediafile):
        self.__set__(mediafile, None)


class CoverArtField(MediaField):
    """A descriptor that provides access to the *raw image data* for the
    cover image on a file. This is used for backwards compatibility: the
    full `ImageListField` provides richer `Image` objects.

    When there are multiple images we try to pick the most likely to be a front
    cover.
    """

    def __init__(self):
        pass

    def __get__(self, mediafile, _):
        candidates = mediafile.images
        if candidates:
            return self.guess_cover_image(candidates).data
        else:
            return None

    @staticmethod
    def guess_cover_image(candidates):
        if len(candidates) == 1:
            return candidates[0]
        try:
            return next(c for c in candidates if c.type == ImageType.front)
        except StopIteration:
            return candidates[0]

    def __set__(self, mediafile, data):
        if data:
            mediafile.images = [Image(data=data)]
        else:
            mediafile.images = []

    def __delete__(self, mediafile):
        delattr(mediafile, "images")


class QNumberField(MediaField):
    """Access integer-represented Q number fields.

    Access a fixed-point fraction as a float. The stored value is shifted by
    `fraction_bits` binary digits to the left and then rounded, yielding a
    simple integer.
    """

    def __init__(self, fraction_bits, *args, **kwargs):
        super().__init__(out_type=int, *args, **kwargs)
        self.__fraction_bits = fraction_bits

    def __get__(self, mediafile, owner=None):
        q_num = super().__get__(mediafile, owner)
        if q_num is None:
            return None
        return q_num / pow(2, self.__fraction_bits)

    def __set__(self, mediafile, value):
        q_num = round(value * pow(2, self.__fraction_bits))
        q_num = int(q_num)  # needed for py2.7
        super().__set__(mediafile, q_num)


class ImageListField(ListMediaField):
    """Descriptor to access the list of images embedded in tags.

    The getter returns a list of `Image` instances obtained from
    the tags. The setter accepts a list of `Image` instances to be
    written to the tags.
    """

    def __init__(self):
        # The storage styles used here must implement the
        # `ListStorageStyle` interface and get and set lists of
        # `Image`s.
        super().__init__(
            MP3ImageStorageStyle(),
            MP4ImageStorageStyle(),
            ASFImageStorageStyle(),
            VorbisImageStorageStyle(),
            FlacImageStorageStyle(),
            APEv2ImageStorageStyle(),
            out_type=Image,
        )
