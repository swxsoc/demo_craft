"""
This module provides errors/exceptions and warnings of general use.

Exceptions that are specific to a given package should **not** be here,
but rather in the particular package.

This code is based on that provided by SunPy see
    licenses/SUNPY.rst
"""
import warnings

__all__ = [
    "craftWarning",
    "craftUserWarning",
    "craftDeprecationWarning",
    "craftPendingDeprecationWarning",
    "warn_user",
    "warn_deprecated",
]


class craftWarning(Warning):
    """
    The base warning class from which all DEMO CRAFT warnings should inherit.

    Any warning inheriting from this class is handled by the DEMO CRAFT
    logger. This warning should not be issued in normal code. Use
    "craftUserWarning" instead or a specific sub-class.
    """


class craftUserWarning(UserWarning, craftWarning):
    """
    The primary warning class for DEMO CRAFT.

    Use this if you do not need a specific type of warning.
    """


class craftDeprecationWarning(FutureWarning, craftWarning):
    """
    A warning class to indicate a deprecated feature.
    """


class craftPendingDeprecationWarning(PendingDeprecationWarning, craftWarning):
    """
    A warning class to indicate a soon-to-be deprecated feature.
    """


def warn_user(msg, stacklevel=1):
    """
    Raise a `craftUserWarning`.

    Parameters
    ----------
    msg : str
        Warning message.
    stacklevel : int
        This is interpreted relative to the call to this function,
        e.g. ``stacklevel=1`` (the default) sets the stack level in the
        code that calls this function.
    """
    warnings.warn(msg, craftUserWarning, stacklevel + 1)


def warn_deprecated(msg, stacklevel=1):
    """
    Raise a `craftDeprecationWarning`.

    Parameters
    ----------
    msg : str
        Warning message.
    stacklevel : int
        This is interpreted relative to the call to this function,
        e.g. ``stacklevel=1`` (the default) sets the stack level in the
        code that calls this function.
    """
    warnings.warn(msg, craftDeprecationWarning, stacklevel + 1)
