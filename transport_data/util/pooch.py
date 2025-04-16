"""Utilities for :mod:`pooch`."""

from collections.abc import Callable
from pathlib import Path
from typing import Optional, Union

import pooch
from pooch.downloaders import DOIDownloader, choose_downloader


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
        self,
        # Args of pooch.Pooch.__init__()
        base_url,
        registry: Union[dict, Path, None] = None,
        urls: Optional[dict] = None,
        retry_if_failed: int = 0,
        allow_updates: bool = True,
        # Additional args
        module: str = "",
        expand: Optional[Callable] = None,
        processor: Optional[str] = None,
    ) -> None:
        kwargs = dict(
            path=pooch.os_cache("transport-data").joinpath(module.split(".")[1]),
            base_url=base_url,
            registry=None if isinstance(registry, Path) else registry,
            urls=urls,
            retry_if_failed=retry_if_failed,
            allow_updates=allow_updates,
        )

        # Identify the Downloader subclass that will be used
        self._downloader_cls = type(choose_downloader(base_url))

        # Store the callback
        self._expand = expand or str

        if processor == "unzip":
            self._processor = pooch.Unzip(extract_dir=kwargs["path"])

        super().__init__(**kwargs)

        # Load registry from a file at the given path
        if isinstance(registry, Path):
            self.load_registry(registry)

    # Override pooch.Pooch methods
    def fetch(self, fname, *args, **kwargs):
        self._ensure_doi_registry()
        kwargs.setdefault("processor", self._processor)
        return super().fetch(self._expand(fname), *args, **kwargs)

    def is_available(self, fname, *args, **kwargs) -> bool:
        self._ensure_doi_registry()
        _fname = self._expand(fname)

        try:
            return super().is_available(_fname, *args, **kwargs)
        except NotImplementedError:
            if self._downloader_cls is DOIDownloader:
                # Override the behaviour of pooch.Pooch. The registry has been
                # downloaded from the upstream source, so assume the advertised files
                # are indeed available.
                return True
            else:
                raise

    # Additional methods
    def _ensure_doi_registry(self) -> None:
        """Ensure that :attr:`registry` is populated for a :class:`DOIDownloader`.

        This calls :meth:`.Pooch.load_registry_from_doi`, but only if the registry has
        not already been loaded.
        """
        if self._downloader_cls is DOIDownloader and not self.registry:
            super().load_registry_from_doi()

    def path_for(self, *args, **kwargs):
        """Return a filename and local cache path for the data file."""
        return self.path.joinpath(self._expand(*args, **kwargs))
