"""Type definitions for MediaFile."""

from typing import Any, TypeAlias

# It is close to impossible to type the Mutagen File
# correctly due to Mutagen's dynamic typing. We might be able
# to create a Protocol that defines the minimum interface
# MediaFile needs, using an alias here should allow us to migrate
# to a more precise type later.
MutagenFile: TypeAlias = Any
