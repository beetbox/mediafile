import functools
import logging
import traceback

import mutagen
import mutagen._util

from mediafile.exceptions import MutagenError, UnreadableFileError

log = logging.getLogger(__name__)


def mutagen_call(action, filename, func, *args, **kwargs):
    """Call a Mutagen function with appropriate error handling.

    `action` is a string describing what the function is trying to do,
    and `filename` is the relevant filename. The rest of the arguments
    describe the callable to invoke.

    We require at least Mutagen 1.33, where `IOError` is *never* used,
    neither for internal parsing errors *nor* for ordinary IO error
    conditions such as a bad filename. Mutagen-specific parsing errors and IO
    errors are reraised as `UnreadableFileError`. Other exceptions
    raised inside Mutagen---i.e., bugs---are reraised as `MutagenError`.
    """
    try:
        return func(*args, **kwargs)
    except mutagen._util.MutagenError as exc:
        log.debug("%s failed: %s", action, str(exc))
        raise UnreadableFileError(filename, str(exc))
    except UnreadableFileError:
        # Reraise our errors without changes.
        # Used in case of decorating functions (e.g. by `loadfile`).
        raise
    except Exception as exc:
        # Isolate bugs in Mutagen.
        log.debug("%s", traceback.format_exc())
        log.error("uncaught Mutagen exception in %s: %s", action, exc)
        raise MutagenError(filename, exc)


def loadfile(method=True, writable=False, create=False):
    """A decorator that works like `mutagen._util.loadfile` but with
    additional error handling.

    Opens a file and passes a `mutagen._utils.FileThing` to the
    decorated function. Should be used as a decorator for functions
    using a `filething` parameter.
    """

    def decorator(func):
        f = mutagen._util.loadfile(method, writable, create)(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return mutagen_call("loadfile", "", f, *args, **kwargs)

        return wrapper

    return decorator


def update_filething(filething):
    """Reopen a `filething` if it's a local file.

    A filething that is *not* an actual file is left unchanged; a
    filething with a filename is reopened and a new object is returned.
    """
    if filething.filename:
        return mutagen._util.FileThing(None, filething.filename, filething.name)
    else:
        return filething
