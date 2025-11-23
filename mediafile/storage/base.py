from mediafile.utils import sc_decode, sc_encode


class StorageStyle:
    """A strategy for storing a value for a certain tag format (or set
    of tag formats). This basic StorageStyle describes simple 1:1
    mapping from raw values to keys in a Mutagen file object; subclasses
    describe more sophisticated translations or format-specific access
    strategies.

    MediaFile uses a StorageStyle via three methods: ``get()``,
    ``set()``, and ``delete()``. It passes a Mutagen file object to
    each.

    Internally, the StorageStyle implements ``get()`` and ``set()``
    using two steps that may be overridden by subtypes. To get a value,
    the StorageStyle first calls ``fetch()`` to retrieve the value
    corresponding to a key and then ``deserialize()`` to convert the raw
    Mutagen value to a consumable Python value. Similarly, to set a
    field, we call ``serialize()`` to encode the value and then
    ``store()`` to assign the result into the Mutagen object.

    Each StorageStyle type has a class-level `formats` attribute that is
    a list of strings indicating the formats that the style applies to.
    MediaFile only uses StorageStyles that apply to the correct type for
    a given audio file.
    """

    formats = [
        "FLAC",
        "OggOpus",
        "OggTheora",
        "OggSpeex",
        "OggVorbis",
        "OggFlac",
        "APEv2File",
        "WavPack",
        "Musepack",
        "MonkeysAudio",
    ]
    """List of mutagen classes the StorageStyle can handle.
    """

    def __init__(self, key, as_type=str, suffix=None, float_places=2, read_only=False):
        """Create a basic storage strategy. Parameters:

        - `key`: The key on the Mutagen file object used to access the
          field's data.
        - `as_type`: The Python type that the value is stored as
          internally (`unicode`, `int`, `bool`, or `bytes`).
        - `suffix`: When `as_type` is a string type, append this before
          storing the value.
        - `float_places`: When the value is a floating-point number and
          encoded as a string, the number of digits to store after the
          decimal point.
        - `read_only`: When true, writing to this field is disabled.
           Primary use case is so wrongly named fields can be addressed
           in a graceful manner. This does not block the delete method.

        """
        self.key = key
        self.as_type = as_type
        self.suffix = suffix
        self.float_places = float_places
        self.read_only = read_only

        # Convert suffix to correct string type.
        if self.suffix and self.as_type is str and not isinstance(self.suffix, str):
            self.suffix = self.suffix.decode("utf-8")

    # Getter.

    def get(self, mutagen_file):
        """Get the value for the field using this style."""
        return self.deserialize(self.fetch(mutagen_file))

    def fetch(self, mutagen_file):
        """Retrieve the raw value of for this tag from the Mutagen file
        object.
        """
        try:
            return mutagen_file[self.key][0]
        except (KeyError, IndexError):
            return None

    def deserialize(self, mutagen_value):
        """Given a raw value stored on a Mutagen object, decode and
        return the represented value.
        """
        if (
            self.suffix
            and isinstance(mutagen_value, str)
            and mutagen_value.endswith(self.suffix)
        ):
            return mutagen_value[: -len(self.suffix)]
        else:
            return mutagen_value

    # Setter.

    def set(self, mutagen_file, value):
        """Assign the value for the field using this style."""
        self.store(mutagen_file, self.serialize(value))

    def store(self, mutagen_file, value):
        """Store a serialized value in the Mutagen file object."""
        mutagen_file[self.key] = [value]

    def serialize(self, value):
        """Convert the external Python value to a type that is suitable for
        storing in a Mutagen file object.
        """
        if isinstance(value, float) and self.as_type is str:
            value = "{0:.{1}f}".format(value, self.float_places)
            value = self.as_type(value)
        elif self.as_type is str:
            if isinstance(value, bool):
                # Store bools as 1/0 instead of True/False.
                value = str(int(bool(value)))
            elif isinstance(value, bytes):
                value = value.decode("utf-8", "ignore")
            else:
                value = str(value)
        else:
            value = self.as_type(value)

        if self.suffix:
            value += self.suffix

        return value

    def delete(self, mutagen_file):
        """Remove the tag from the file."""
        if self.key in mutagen_file:
            del mutagen_file[self.key]


class ListStorageStyle(StorageStyle):
    """Abstract storage style that provides access to lists.

    The ListMediaField descriptor uses a ListStorageStyle via two
    methods: ``get_list()`` and ``set_list()``. It passes a Mutagen file
    object to each.

    Subclasses may overwrite ``fetch`` and ``store``.  ``fetch`` must
    return a (possibly empty) list or `None` if the tag does not exist.
    ``store`` receives a serialized list of values as the second argument.

    The `serialize` and `deserialize` methods (from the base
    `StorageStyle`) are still called with individual values. This class
    handles packing and unpacking the values into lists.
    """

    def get(self, mutagen_file):
        """Get the first value in the field's value list."""
        values = self.get_list(mutagen_file)
        if values is None:
            return None

        try:
            return values[0]
        except IndexError:
            return None

    def get_list(self, mutagen_file):
        """Get a list of all values for the field using this style."""
        raw_values = self.fetch(mutagen_file)
        if raw_values is None:
            return None

        return [self.deserialize(item) for item in raw_values]

    def fetch(self, mutagen_file):
        """Get the list of raw (serialized) values."""
        try:
            return mutagen_file[self.key]
        except KeyError:
            return None

    def set(self, mutagen_file, value):
        """Set an individual value as the only value for the field using
        this style.
        """
        if value is None:
            self.store(mutagen_file, None)
        else:
            self.set_list(mutagen_file, [value])

    def set_list(self, mutagen_file, values):
        """Set all values for the field using this style. `values`
        should be an iterable.
        """
        if values is None:
            self.delete(mutagen_file)
        else:
            self.store(mutagen_file, [self.serialize(value) for value in values])

    def store(self, mutagen_file, values):
        """Set the list of all raw (serialized) values for this field."""
        mutagen_file[self.key] = values


class SoundCheckStorageStyleMixin:
    """A mixin for storage styles that read and write iTunes SoundCheck
    analysis values. The object must have an `index` field that
    indicates which half of the gain/peak pair---0 or 1---the field
    represents.
    """

    def get(self, mutagen_file):
        data = self.fetch(mutagen_file)
        if data is not None:
            return sc_decode(data)[self.index]

    def set(self, mutagen_file, value):
        data = self.fetch(mutagen_file)
        if data is None:
            gain_peak = [0, 0]
        else:
            gain_peak = list(sc_decode(data))
        gain_peak[self.index] = value or 0
        data = self.serialize(sc_encode(*gain_peak))
        self.store(mutagen_file, data)
