from typing import Callable

import pooch


class Pooch(pooch.Pooch):
    """:class:`pooch.Pooch` with special powers.

    Parameters
    ----------
    module : str
        The `path` argument to pooch.Pooch is derived automatically from this, within
        the transport-data directory.
    expand : callable, optional
        If given, a function that receives any argument and returns a file name found
        within the Pooch registry.
    processor :
        If the exact value "unzip", fetch() operations are always processed to unzip
        archive contents into the same directory as the downloaded file.
    """

    _processor = None

    def __init__(
        self, *args, module: str, expand: Callable = None, processor=None, **kwargs
    ):
        kwargs.setdefault(
            "path", pooch.os_cache("transport-data").joinpath(module.split(".")[1])
        )

        self._expand = expand or str

        if processor == "unzip":
            self._processor = pooch.Unzip(extract_dir=kwargs["path"])

        super().__init__(*args, **kwargs)

    def fetch(self, fname, *args, **kwargs):
        kwargs.setdefault("processor", self._processor)
        return super().fetch(self._expand(fname), *args, **kwargs)

    def is_available(self, fname, *args, **kwargs):
        return super().is_available(self._expand(fname), *args, **kwargs)
