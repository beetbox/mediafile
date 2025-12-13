import re
from typing import Any, TypeVar, cast

T = TypeVar("T")


def safe_cast(out_type: type[T], val: Any) -> T | None:
    """Try to covert val to out_type but never raise an exception.

    If the value does not exist, return None. Or, if the value
    can't be converted, then a sensible default value is returned.
    out_type should be bool, int, or unicode; otherwise, the value
    is just passed through.
    """
    if val is None:
        return None

    if out_type is int:
        if isinstance(val, int) or isinstance(val, float):
            # Just a number.
            return cast(T, int(val))
        else:
            # Process any other type as a string.
            if isinstance(val, bytes):
                val = val.decode("utf-8", "ignore")
            elif not isinstance(val, str):
                val = str(val)
            # Get a number from the front of the string.
            match = re.match(r"[\+-]?[0-9]+", val.strip())
            return cast(T, int(match.group(0))) if match else cast(T, 0)

    elif out_type is bool:
        try:
            # Should work for strings, bools, ints:
            return cast(T, bool(int(val)))
        except ValueError:
            return cast(T, False)

    elif out_type is str:
        if isinstance(val, bytes):
            return cast(T, val.decode("utf-8", "ignore"))
        elif isinstance(val, str):
            return cast(T, val)
        else:
            return cast(T, str(val))

    elif out_type is float:
        if isinstance(val, int) or isinstance(val, float):
            return cast(T, float(val))
        else:
            if isinstance(val, bytes):
                val = val.decode("utf-8", "ignore")
            else:
                val = str(val)
            match = re.match(r"[\+-]?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+)", val.strip())
            if match:
                val = match.group(0)
                if val:
                    return cast(T, float(val))
            return cast(T, 0.0)

    else:
        return cast(T, val)


def safe_cast_list(out_type: type[T], val: list[Any] | None) -> list[T] | None:
    """Cast a value to a list of out_type elements, or None.

    If the value is None or, return None. If the value is already a list or
    tuple, cast each element to out_type.
    """
    if val is None:
        return None

    if isinstance(val, (list, tuple)):
        return list(filter(None, (safe_cast(out_type, v) for v in val)))

    raise ValueError("Value is not a list or tuple")
