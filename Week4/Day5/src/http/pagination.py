# Minimal RFC5988 Link header parser:  <url>; rel="next", <url>; rel="last"
from typing import Dict

def parse_link_header(link_value: str) -> Dict[str, dict]:
    result: Dict[str, dict] = {}
    if not link_value:
        return result
    parts = [p.strip() for p in link_value.split(",")]
    for part in parts:
        if ">;" not in part:
            continue
        url_part, rest = part.split(">;", 1)
        url = url_part.strip()[1:]  # drop leading '<'
        rel = None
        for token in rest.split(";"):
            token = token.strip()
            if token.startswith("rel="):
                rel = token.split("=", 1)[1].strip().strip('"')
        if rel:
            result[rel] = {"url": url}
    return result
