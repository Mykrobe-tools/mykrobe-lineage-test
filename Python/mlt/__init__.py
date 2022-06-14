from pkg_resources import get_distribution

try:
    __version__ = get_distribution("mlt").version
except:
    __version__ = "local"


__all__ = [
    "samples",
    "tasks",
    "utils",
]

from mlt import *
