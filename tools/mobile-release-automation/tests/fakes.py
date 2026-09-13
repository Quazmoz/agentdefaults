"""In-memory HTTP doubles so the toolkit's logic can be tested offline."""

from __future__ import annotations

from typing import Any, Callable
import json


class FakeResponse:
    def __init__(self, status_code: int = 200, payload: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text or json.dumps(payload or {})

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def content(self) -> bytes:
        return self.text.encode("utf-8")

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("no json body")
        return self._payload


class FakeSession:
    """Routes (method, url-substring) to a handler and records every call."""

    def __init__(self, routes: dict[tuple[str, str], Callable[..., FakeResponse]]) -> None:
        self.routes = routes
        self.calls: list[dict[str, Any]] = []
        self.headers: dict[str, str] = {}

    def request(self, method: str, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": method.upper(), "url": url, **kwargs})
        matches = [
            (fragment, handler)
            for (route_method, fragment), handler in self.routes.items()
            if route_method == method.upper() and fragment in url
        ]
        if not matches:
            raise AssertionError(f"unrouted request: {method.upper()} {url}")
        # Longest fragment wins, so "/edits/x/bundles" beats a generic "/edits".
        _, handler = max(matches, key=lambda match: len(match[0]))
        return handler(url=url, **kwargs)

    def post(self, url: str, **kwargs) -> FakeResponse:
        return self.request("POST", url, **kwargs)

    def get(self, url: str, **kwargs) -> FakeResponse:
        return self.request("GET", url, **kwargs)

    def delete(self, url: str, **kwargs) -> FakeResponse:
        return self.request("DELETE", url, **kwargs)

    def urls(self, method: str | None = None) -> list[str]:
        return [
            call["url"]
            for call in self.calls
            if method is None or call["method"] == method.upper()
        ]

    def body_for(self, method: str, fragment: str) -> Any:
        for call in self.calls:
            if call["method"] == method.upper() and fragment in call["url"]:
                return call.get("json")
        raise AssertionError(f"no recorded {method} call matching {fragment!r}")


def ok(payload: Any) -> Callable[..., FakeResponse]:
    return lambda **_: FakeResponse(200, payload)


def fail(status_code: int, payload: Any = None) -> Callable[..., FakeResponse]:
    return lambda **_: FakeResponse(status_code, payload or {"error": {"message": "denied"}})
