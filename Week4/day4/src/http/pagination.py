# src/http/pagination.py (append or replace your function)
from __future__ import annotations
from typing import Any, Callable, Dict, Generator, Optional, Tuple
import requests

PageValidator = Callable[[Any], None]
PageTransform = Callable[[Any], Any]

def _extract_container(data: Any, keys: Tuple[str, ...] = ("data", "results", "items")) -> Optional[list]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys:
            v = data.get(k)
            if isinstance(v, list):
                return v
    return None

def _infer_total_pages(data: Any) -> Optional[int]:
    """Look for common pagination hints in response bodies."""
    if not isinstance(data, dict):
        return None
    for k in ("total_pages", "pages", "last_page"):
        if isinstance(data.get(k), int):
            return int(data[k])
    # Some APIs give total items + page size
    if isinstance(data.get("total"), int) and isinstance(data.get("per_page") or data.get("page_size"), int):
        total = int(data["total"])
        per = int(data.get("per_page") or data.get("page_size"))
        if per > 0:
            # ceil division
            return (total + per - 1) // per
    return None

def paginate_page_limit(
    base_url: str,
    *,
    start_page: int = 1,
    limit: int = 100,
    extra_params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 15.0,
    validator: Optional[PageValidator] = None,
    transform: Optional[PageTransform] = None,
    validate_after_transform: bool = False,
    max_pages: Optional[int] = None,
    stop_on_short_page: bool = True,
    page_param_name: str = "page",
    limit_param_name: str = "limit",  # change to "per_page" if needed
) -> Generator[Any, None, None]:
    """
    Yield numbered pages: ?page=N&limit=K (param names configurable).
    Stops on empty page, or short page (optional), or after max_pages.
    Also respects total_pages if the API provides it.
    """
    ses = requests.Session()
    page = start_page
    fetched_pages = 0
    extra_params = dict(extra_params or {})
    known_total_pages: Optional[int] = None

    while True:
        params = {page_param_name: page, limit_param_name: limit, **extra_params}
        resp = ses.get(base_url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        # discover total_pages once (if present)
        if known_total_pages is None:
            known_total_pages = _infer_total_pages(data)

        # validate/transform in desired order
        if validate_after_transform and transform:
            data = transform(data)
            if validator:
                validator(data)
        else:
            if validator:
                validator(data)
            if transform:
                data = transform(data)

        yield data
        fetched_pages += 1

        # empty or short page stop conditions
        container = _extract_container(data)
        is_empty = (isinstance(container, list) and len(container) == 0) or (isinstance(data, list) and len(data) == 0)
        if is_empty:
            break
        if stop_on_short_page and container is not None and len(container) < limit:
            break

        # honor known total pages
        if known_total_pages is not None and page >= known_total_pages:
            break

        if max_pages and fetched_pages >= max_pages:
            break

        page += 1

from typing import Iterable

def iter_page_items(
    base_url: str,
    *,
    start_page: int = 1,
    limit: int = 100,
    item_key_candidates: Tuple[str, ...] = ("data", "results", "items"),
    id_key: Optional[str] = "id",
    max_items: Optional[int] = None,
    dedupe_capacity: int = 20000,  # safety cap on seen set (avoid unlimited RAM)
    **kwargs
) -> Generator[dict, None, None]:
    """
    Stream items across all numbered pages, optionally de-duplicating by `id_key`.
    """
    seen: set = set()
    yielded = 0

    for page in paginate_page_limit(base_url, start_page=start_page, limit=limit, **kwargs):
        container = _extract_container(page, item_key_candidates)
        if not container:
            continue

        for item in container:
            if id_key and isinstance(item, dict) and id_key in item:
                _id = item[id_key]
                if _id in seen:
                    continue
                if len(seen) < dedupe_capacity:
                    seen.add(_id)

            yield item
            yielded += 1
            if max_items and yielded >= max_items:
                return
from urllib.parse import urlparse, parse_qs

def paginate(
    url: str,
    *,
    mode: Optional[str] = None,  # "cursor" | "page" | None (auto)
    timeout: float = 15.0,
    **kwargs
) -> Iterable[Any]:
    """
    Auto route to cursor or page/limit iterator.
    If `mode` unset, probe the first response for body['next'] or Link header.
    """
    if mode == "cursor":
        from .pagination import paginate_cursor  # local import to avoid cycles
        return paginate_cursor(url, timeout=timeout, **kwargs)
    if mode == "page":
        # If `url` already includes page params, split base & feed paginate_page_limit
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        qs = parse_qs(parsed.query)
        start_page = int(qs.get("page", [kwargs.pop("start_page", 1)])[0])
        limit = int(qs.get("limit", qs.get("per_page", [kwargs.pop("limit", 100)]))[0])
        return paginate_page_limit(base_url, start_page=start_page, limit=limit, timeout=timeout, **kwargs)

    # Auto-detect by probing first page
    session = requests.Session()
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    body = resp.json()

    # Body 'next' → cursor mode
    if isinstance(body, dict) and (body.get("next") or body.get("next_url")):
        def gen():
            # yield the inspected page (respect transform/validator order)
            validator = kwargs.get("validator")
            transform = kwargs.get("transform")
            validate_after_transform = kwargs.get("validate_after_transform", False)

            data = body
            if validate_after_transform and transform:
                data = transform(data)
                if validator:
                    validator(data)
            else:
                if validator:
                    validator(data)
                if transform:
                    data = transform(data)
            yield data

            # continue with cursor pagination starting from the resolved URL
            from .pagination import paginate_cursor
            for p in paginate_cursor(resp.url, timeout=timeout, **{k: v for k, v in kwargs.items() if k not in ("validator", "transform", "validate_after_transform")}):
                yield p
        return gen()

    # Link rel="next" → cursor mode
    if resp.headers.get("Link") or resp.headers.get("link"):
        from .pagination import paginate_cursor
        def gen():
            yield body
            for p in paginate_cursor(resp.url, timeout=timeout, **kwargs):
                yield p
        return gen()

    # Otherwise expect page/limit
    return paginate_page_limit(url, timeout=timeout, **kwargs)
