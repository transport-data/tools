"""Utilities for :mod:`responses`."""

from typing import TYPE_CHECKING, Any

import responses

if TYPE_CHECKING:
    from responses import BaseResponse, PreparedRequest


class RepeatRegistry(responses.FirstMatchRegistry):
    """Response registry that repeats the same response for each URL infinitely."""

    def find(
        self, request: "PreparedRequest"
    ) -> tuple["BaseResponse | None", list[str]]:
        found = None
        found_match = None
        match_failed_reasons = []
        for i, response in enumerate(self.registered):
            match_result, reason = response.matches(request)
            if match_result:
                if found is None:
                    found = i
                    found_match = response
                else:
                    # Parent class uses self.registered.pop() below
                    if self.registered[found].call_count > 0:
                        found_match = response
                        break
                    # Multiple matches found → return the first response
                    return self.registered[found], match_failed_reasons
            else:
                match_failed_reasons.append(reason)
        return found_match, match_failed_reasons


class RequestsMock(responses.RequestsMock):
    """RequestsMock that does not reset on context manager exit."""

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        success = type is None
        self.stop(allow_assert=success)
