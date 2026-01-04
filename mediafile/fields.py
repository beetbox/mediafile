from __future__ import annotations

# MediaField is a descriptor that represents a single logical field. It
# aggregates several StorageStyles describing how to access the data for
# each file type.
import datetime
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Generic

from typing_extensions import TypeVar

from mediafile.constants import null_value
from mediafile.utils import Image, safe_cast
from mediafile.utils.type_conversion import safe_cast_list

from ._types import MutagenFile
from .constants import ImageType
from .storage import (
    APEv2ImageStorageStyle,
    ASFImageStorageStyle,
    FlacImageStorageStyle,
    ListStorageStyle,
    MP3ImageStorageStyle,
    MP4ImageStorageStyle,
    StorageStyle,
    VorbisImageStorageStyle,
)

if TYPE_CHECKING:
    from . import MediaFile

T = TypeVar("T", default=str)
S = TypeVar("S", bound=StorageStyle, default=StorageStyle)
DEFAULT_OUT_TYPE: type = str


class BaseMediaField(ABC, Generic[T, S]):
    """Abstract base class for media file metadata field descriptors.

    Subclasses must implement the ``__get__``, ``__set__``, and
    ``__delete__`` methods.
    """

    _styles: Sequence[S]

    def styles(self, mutagen_file: MutagenFile) -> Iterable[S]:
        """Yields the list of storage styles of this field that can
        handle the MediaFile's format.
        """
        for style in self._styles:
            if mutagen_file.__class__.__name__ in style.formats:
                yield style

    @abstractmethod
    def __get__(self, mediafile: MediaFile, owner: object = None) -> T | None: ...

    @abstractmethod
    def __set__(self, mediafile: MediaFile, value: T | None) -> None: ...

    def __delete__(self, mediafile: MediaFile) -> None:
        for style in self.styles(mediafile.mgfile):
            style.delete(mediafile.mgfile)


def _set_data_in_styles(
    value: T | None,
    mediafile: MediaFile,
    styles: Iterable[StorageStyle],
    out_type: type[T],
) -> None:
    """Helpers to set data in multiple styles.

    Mainly created to avoid code duplication and keep type checking happy.
    """

    if value is None:
        value = null_value(out_type)
    for style in styles:
        if not style.read_only:
            style.set(mediafile.mgfile, value)


def _get_data_from_styles(
    mediafile: MediaFile,
    styles: Iterable[StorageStyle],
    out_type: type[T],
) -> T | None:
    """Helper to get data from multiple styles.

    Mainly created to avoid code duplication and keep type checking happy.
    """
    out = None
    for style in styles:
        out = style.get(mediafile.mgfile)
        if out:
            break
    return safe_cast(out_type, out)


class MediaField(BaseMediaField[T, StorageStyle]):
    """A descriptor providing access to a particular (abstract) metadata
    field.
    """

    out_type: type[T]

    def __init__(
        self,
        *styles: StorageStyle,
        out_type: type[T] = DEFAULT_OUT_TYPE,
    ):
        """Creates a new MediaField.

        :param styles: `StorageStyle` instances that describe the strategy
                       for reading and writing the field in particular
                       formats. There must be at least one style for
                       each possible file format.

        :param out_type: the type of the value that should be returned when
                         getting this property.

        """
        self.out_type = out_type
        self._styles = styles

    def __get__(self, mediafile: MediaFile, owner: object | None = None) -> T | None:
        return _get_data_from_styles(
            mediafile,
            self.styles(mediafile.mgfile),
            self.out_type,
        )

    def __set__(self, mediafile: MediaFile, value: T | None) -> None:
        return _set_data_in_styles(
            value,
            mediafile,
            self.styles(mediafile.mgfile),
            self.out_type,
        )


class ListMediaField(BaseMediaField[list[T], ListStorageStyle]):
    """Property descriptor that retrieves a list of multiple values from
    a tag.

    Uses ``get_list`` and set_list`` methods of its ``StorageStyle``
    strategies to do the actual work.
    """

    _styles: Sequence[ListStorageStyle]

    def __init__(
        self,
        *styles: ListStorageStyle,
        out_type: type[T] = DEFAULT_OUT_TYPE,
    ):
        """Creates a new ListMediaField.

        :param styles: `ListStorageStyle` instances that describe the
                       strategy for reading and writing the field in
                       particular formats. There must be at least one
                       style for each possible file format.

        :param out_type: the type of the elements in the list that
                         should be returned when getting this property.

        """
        self.out_type = out_type
        self._styles = styles

    def __get__(
        self, mediafile: MediaFile, owner: object | None = None
    ) -> list[T] | None:
        """Returns the list of values, or None if no values are set.

        Note: the list is always non-empty when returned; if the underlying
        styles return an empty list, None is returned instead.
        """
        for style in self.styles(mediafile.mgfile):
            values = style.get_list(mediafile.mgfile)
            return safe_cast_list(self.out_type, values) or None
        return None

    def __set__(self, mediafile: MediaFile, values: list[T] | None) -> None:
        for style in self.styles(mediafile.mgfile):
            if not style.read_only:
                style.set_list(mediafile.mgfile, values)

    def single_field(self) -> MediaField[T]:
        """Returns a ``MediaField`` descriptor that gets and sets the
        first item.
        """
        options = {"out_type": self.out_type}
        return MediaField(*self._styles, **options)


class DateField(BaseMediaField[datetime.date, StorageStyle]):
    """Descriptor that handles serializing and deserializing dates

    The getter parses value from tags into a ``datetime.date`` instance
    and setter serializes such an instance into a string.

    For granular access to year, month, and day, use the ``*_field``
    methods to create corresponding `DateItemField`s.
    """

    def __init__(
        self,
        *date_styles: StorageStyle,
        year: Sequence[StorageStyle] | None = None,
    ):
        """``date_styles`` is a list of ``StorageStyle``s to store and
        retrieve the whole date from. The ``year`` option is an
        additional list of fallback styles for the year. The year is
        always set on this style, but is only retrieved if the main
        storage styles do not return a value.
        """
        # The OOP pattern is janky here, while
        # the base class should handle strings
        self._styles = date_styles
        if year is not None:
            self._year_field = MediaField(*year, out_type=str)

    def __get__(
        self, mediafile: MediaFile, owner: object | None = None
    ) -> None | datetime.date:
        year, month, day = self._get_date_tuple(mediafile)
        if not year:
            return None
        try:
            return datetime.date(year, month or 1, day or 1)
        except ValueError:  # Out of range values.
            return None

    def __set__(self, mediafile: MediaFile, date: datetime.date | None) -> None:
        if date is None:
            self._set_date_tuple(mediafile, None, None, None)
        else:
            self._set_date_tuple(mediafile, date.year, date.month, date.day)

    def __delete__(self, mediafile: MediaFile) -> None:
        super().__delete__(mediafile)
        if hasattr(self, "_year_field"):
            self._year_field.__delete__(mediafile)

    def _get_date_tuple(self, mediafile: MediaFile) -> list[int | None]:
        """Get a 3-item sequence representing the date consisting of a
        year, month, and day number.
        """
        # Get the underlying data as string
        datestring = _get_data_from_styles(
            mediafile,
            self.styles(mediafile.mgfile),
            str,
        )

        # Split the date string into components.
        items: list[str | None]
        if datestring:
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
        return [int(x) if x and x.isdigit() else None for x in items]

    def _set_date_tuple(
        self,
        mediafile: MediaFile,
        year: int | None,
        month: int | None = None,
        day: int | None = None,
    ) -> None:
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

        _set_data_in_styles(
            "-".join(map(str, date)),
            mediafile,
            self.styles(mediafile.mgfile),
            str,
        )

        if hasattr(self, "_year_field"):
            self._year_field.__set__(mediafile, safe_cast(str, year))

    def year_field(self) -> DateItemField:
        return DateItemField(self, 0)

    def month_field(self) -> DateItemField:
        return DateItemField(self, 1)

    def day_field(self) -> DateItemField:
        return DateItemField(self, 2)


class DateItemField(MediaField[int]):
    """Descriptor that gets and sets constituent parts of a `DateField`:
    the month, day, or year.
    """

    def __init__(self, date_field: DateField, item_pos: int):
        self.date_field = date_field
        self.item_pos = item_pos
        super().__init__(out_type=int)

    def __get__(self, mediafile: MediaFile, owner: object | None = None) -> int | None:
        return self.date_field._get_date_tuple(mediafile)[self.item_pos]

    def __set__(self, mediafile: MediaFile, value: int | None) -> None:
        items = self.date_field._get_date_tuple(mediafile)
        items[self.item_pos] = value
        self.date_field._set_date_tuple(mediafile, *items)

    def __delete__(self, mediafile: MediaFile) -> None:
        self.__set__(mediafile, None)


class CoverArtField(MediaField[bytes]):
    """A descriptor that provides access to the *raw image data* for the
    cover image on a file. This is used for backwards compatibility: the
    full `ImageListField` provides richer `Image` objects.

    When there are multiple images we try to pick the most likely to be a front
    cover.
    """

    def __init__(self) -> None:
        pass

    def __get__(
        self, mediafile: MediaFile, owner: object | None = None
    ) -> bytes | None:
        candidates = mediafile.images
        if candidates:
            return self.guess_cover_image(candidates).data
        else:
            return None

    @staticmethod
    def guess_cover_image(candidates: list[Image]) -> Image:
        if len(candidates) == 1:
            return candidates[0]
        try:
            return next(c for c in candidates if c.type == ImageType.front)
        except StopIteration:
            return candidates[0]

    def __set__(self, mediafile: MediaFile, data: bytes | None) -> None:
        if data:
            mediafile.images = [Image(data=data)]
        else:
            mediafile.images = []

    def __delete__(self, mediafile: MediaFile) -> None:
        delattr(mediafile, "images")


class QNumberField(MediaField[float]):
    """Access integer-represented Q number fields.

    Access a fixed-point fraction as a float. The stored value is shifted by
    `fraction_bits` binary digits to the left and then rounded, yielding a
    simple integer.
    """

    __fraction_bits: int

    def __init__(
        self,
        fraction_bits: int,
        *styles: StorageStyle,
    ):
        super().__init__(
            *styles,
            out_type=int,
        )
        self.__fraction_bits = fraction_bits

    def __get__(
        self, mediafile: MediaFile, owner: object | None = None
    ) -> float | None:
        q_num: int | None = super().__get__(mediafile, owner)  # type: ignore[assignment]
        if q_num is None:
            return None
        return q_num / 2**self.__fraction_bits  # type: ignore[no-any-return]

    def __set__(self, mediafile: MediaFile, value: float | None) -> None:
        if value is not None:
            value = round(value * 2**self.__fraction_bits)
        super().__set__(mediafile, value)


class ImageListField(ListMediaField[Image]):
    """Descriptor to access the list of images embedded in tags.

    The getter returns a list of `Image` instances obtained from
    the tags. The setter accepts a list of `Image` instances to be
    written to the tags.
    """

    def __init__(self) -> None:
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
