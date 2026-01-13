"""Utilities for :mod:`pooch`."""

import logging
import time
from collections.abc import Callable
from functools import cache, partial
from http import HTTPStatus
from pathlib import Path

import pooch
import pooch.downloaders
from pooch.downloaders import (
    DEFAULT_TIMEOUT,
    DataRepository,
    DataverseRepository,
    FigshareRepository,
    HTTPDownloader,
    choose_downloader,
)
from pooch.utils import parse_url

log = logging.getLogger(__name__)


class DOIDownloader(pooch.downloaders.DOIDownloader):
    def __call__(self, url: str, output_file, pooch: "Pooch") -> None:
        from requests.exceptions import HTTPError

        # NB Identical to the upstream version, except use the Pooch._repository
        #    attribute. This avoids repeatedly querying the API.
        data_repository = pooch._repository
        assert data_repository is not None

        # Resolve the URL; remove a leading slash in the path
        file_name = parse_url(url)["path"].lstrip("/")
        download_url = data_repository.download_url(file_name)

        # Possibly append request headers, e.g. with a Zenodo API token
        kwargs = self.kwargs.copy()
        if pooch._repository and hasattr(pooch._repository, "get_headers"):
            kwargs.setdefault("headers", {})
            kwargs["headers"] |= pooch._repository.get_headers()

        # Instantiate the downloader object
        downloader = HTTPDownloader(
            progressbar=self.progressbar, chunk_size=self.chunk_size, **kwargs
        )
        retry(
            partial(downloader, download_url, output_file, pooch),
            lambda r: not isinstance(r, HTTPError),
        )


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

    _downloader_cls: type
    _processor = None
    _repository: "DataRepository | None" = None

    def __init__(
        self,
        # Args of pooch.Pooch.__init__()
        base_url,
        registry: dict | Path | None = None,
        urls: dict | None = None,
        retry_if_failed: int = 0,
        allow_updates: bool = True,
        # Additional args
        module: str = "",
        expand: Callable | None = None,
        processor: str | None = None,
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
        # Use the modified DOIDownloader from the current module
        if issubclass(DOIDownloader, self._downloader_cls):
            self._downloader_cls = DOIDownloader

        # Store the callback
        self._expand = expand or str

        if processor == "unzip":
            self._processor = pooch.Unzip(extract_dir=kwargs["path"])

        super().__init__(**kwargs)

        # Load registry from a file at the given path
        if isinstance(registry, Path):
            self.load_registry(registry)

    # Override pooch.Pooch methods
    def fetch(self, fname: str, *args, **kwargs) -> str:
        self._ensure_doi_registry()

        fname = self._expand(fname)
        kwargs.setdefault(
            "downloader",
            self._downloader_cls(progressbar=kwargs.get("progressbar", False)),
        )
        kwargs.setdefault("processor", self._processor)
        return super().fetch(fname, *args, **kwargs)

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
            else:  # pragma: no cover
                raise

    # Additional methods
    def _ensure_doi_registry(self) -> None:
        """Ensure that :attr:`registry` is populated for a :class:`DOIDownloader`.

        This version differs from the parent class in calling
        :meth:`.Pooch.load_registry_from_doi` only if the registry has not already been
        loaded.
        """
        self.load_registry_from_doi()

    def load_registry_from_doi(self) -> None:
        """Populate the registry using the data repository API.

        This version differs from the parent class in using :func:`doi_to_repository`
        from the current module.
        """
        if self._downloader_cls is not DOIDownloader:
            return
        elif self.registry:
            return

        if self._repository is None:
            # Create a repository instance
            doi = self.base_url.replace("doi:", "")
            self._repository = doi_to_repository(doi)

        # Call registry population for this repository
        return self._repository.populate_registry(self)

    def path_for(self, *args, **kwargs):
        """Return a filename and local cache path for the data file."""
        return self.path.joinpath(self._expand(*args, **kwargs))


def retry(func: Callable, check: Callable):
    """Retry `func` until :py:`check(func())` returns :any:`True`."""
    msg = f"Got HTTP {HTTPStatus.TOO_MANY_REQUESTS} Too Many Requests"

    # Some Fibonacci numbers for delays
    for wait in (1, 2, 3, 5, 8, 13, 21, 34, 55, 89):
        try:
            result = func()
        except Exception as e:
            # func() raised an exception; pass this to check()
            result = e

        if check(result):
            return result
        else:
            log.warning(f"{msg}; retrying in {wait} s")

            time.sleep(wait)

    raise RuntimeError(msg)


class ZenodoRepository(pooch.downloaders.ZenodoRepository):
    """Custom version of :class:`pooch.downloaders.ZenodoRepository`."""

    @property
    def api_response(self):
        """Cached API response from Zenodo.

        This version differs from the upstream version:

        1. The record ID for the Zenodo API is constructed without the "zenodo." prefix.
        2. A keyring secret with ID ``api-token-zenodo``, if any, is used for the HTTP
           “Authorization” header.
        3. The request is retried with increasing delays until it succeeds.
        """
        from requests.exceptions import JSONDecodeError

        if self._api_response is None:
            import requests

            # Separate the Zenodo record ID from the full URL
            record_id = self.archive_url.rpartition("/zenodo.")[2]
            assert record_id.isdigit()  # The ID is always numeric
            url = f"{self.base_api_url}/{record_id}"

            # Maybe retrieve some headers including the Zenodo API token
            headers = self.get_headers()

            response = retry(
                partial(requests.get, url, timeout=DEFAULT_TIMEOUT, headers=headers),
                lambda r: r.status_code != HTTPStatus.TOO_MANY_REQUESTS,
            )

            try:
                self._api_response = response.json()
            except JSONDecodeError:  # pragma: no cover
                raise RuntimeError(
                    f"Received {response} from {url} with headers:\n"
                    f"{response.headers}\nand body:\n{response.content}"
                )

        return self._api_response

    @classmethod
    @cache
    def get_headers(cls) -> dict[str, str]:
        """Return a set of HTTP headers including the Zenodo API token, if any."""
        try:
            import keyring
        except ImportError:  # pragma: no cover
            pass
        else:
            if token := keyring.get_password("transport-data", "api-token-zenodo"):
                log.info("Using Zenodo API token from keyring")
                return {"Authorization": f"Bearer {token}"}
        return {}


def doi_to_repository(doi: str) -> "DataRepository":
    """Instantiate a data repository instance from a given DOI.

    This version differs from the upstream version in using :func:`doi_to_url` and
    :class:`ZenodoRepository` from the current module.
    """
    doi = doi.rstrip("/")

    # Construct a direct URL to the archive/record from the DOI
    archive_url = doi_to_url(doi)

    # Try the converters one by one until one of them returns a URL
    for cls in (FigshareRepository, ZenodoRepository, DataverseRepository):
        if data_repository := cls.initialize(archive_url=archive_url, doi=doi):
            return data_repository

    raise ValueError(f"Cannot construct a repository for DOI:{doi}")


def doi_to_url(doi: str) -> str:
    """Follow a DOI link to resolve the URL of the archive.

    This version differs from the upstream version in only making a single request, to
    doi.org. The HTTP 302 (redirect) response has a "location" header that gives the
    resolved URL for the DOI; this is returned directly and not queried.
    """
    import requests

    response = requests.get(
        f"https://doi.org/{doi}", timeout=DEFAULT_TIMEOUT, allow_redirects=False
    )
    assert response.status_code == HTTPStatus.FOUND
    return response.headers["location"]
