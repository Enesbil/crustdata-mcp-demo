from urllib.parse import urlencode
from typing import Optional, Any

from crustdata_mcp_demo.constants import API_BASE_URL
from crustdata_mcp_demo.models import DryRunResult


def build_request(
    method: str,
    path: str,
    params: Optional[dict] = None,
    json_body: Optional[Any] = None,
) -> DryRunResult:
    url = f"{API_BASE_URL}{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url = f"{url}?{urlencode(filtered)}"

    headers = {
        "Accept": "application/json",
        "Authorization": "Token $token",
    }
    if json_body is not None:
        headers["Content-Type"] = "application/json"

    return DryRunResult(
        method=method,
        url=url,
        headers=headers,
        body=json_body,
    )
