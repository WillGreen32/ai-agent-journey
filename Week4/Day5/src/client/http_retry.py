from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def build_retry_adapter(
    total=3,
    backoff_factor=0.6,
    status_forcelist=(429, 500, 502, 503, 504),
):
    retry = Retry(
        total=total, read=total, connect=total, status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "HEAD"]),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry)
