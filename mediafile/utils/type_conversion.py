import re


def safe_cast(out_type, val):
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
            return int(val)
        else:
            # Process any other type as a string.
            if isinstance(val, bytes):
                val = val.decode("utf-8", "ignore")
            elif not isinstance(val, str):
                val = str(val)
            # Get a number from the front of the string.
            match = re.match(r"[\+-]?[0-9]+", val.strip())
            return int(match.group(0)) if match else 0

    elif out_type is bool:
        try:
            # Should work for strings, bools, ints:
            return bool(int(val))
        except ValueError:
            return False

    elif out_type is str:
        if isinstance(val, bytes):
            return val.decode("utf-8", "ignore")
        elif isinstance(val, str):
            return val
        else:
            return str(val)

    elif out_type is float:
        if isinstance(val, int) or isinstance(val, float):
            return float(val)
        else:
            if isinstance(val, bytes):
                val = val.decode("utf-8", "ignore")
            else:
                val = str(val)
            match = re.match(r"[\+-]?([0-9]+\.?[0-9]*|[0-9]*\.[0-9]+)", val.strip())
            if match:
                val = match.group(0)
                if val:
                    return float(val)
            return 0.0

    else:
        return val
