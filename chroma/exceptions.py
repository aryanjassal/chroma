class VersionMismatchException(Exception):
    """
    Thrown when the installed Chroma's version does not match the requried
    version by the theme. This means that your version of Chroma is too old for
    that theme, or the theme writer is an idiot and requires a version which
    doesn't even exist yet.
    """
    pass


class InvalidFieldException(Exception):
    """
    Thrown when a field or an option deviates from the expected format.
    """
    pass


# TODO: Make sure there is no need for this exception and the program handles
# everything on its own.
class ParentDirectoryException(Exception):
    """
    Thrown when the parent directory leading to an output theme file doesn't
    exist. Make sure to go back and make the leading directory to a theme.
    """
    pass


class ProgramNotFoundException(Exception):
    """
    Thrown when an expected program isn't found on the host system. Please
    install it before running the program again.
    """
    pass


# TODO: Similar error probably exists somewhere. If it does, use that.
class InvalidModuleException(Exception):
    """
    Thrown when a module failed to load. This means that the module doesn't
    contain valid Python code or isn't designed to be importable. Fix the
    file which failed to import.
    """
