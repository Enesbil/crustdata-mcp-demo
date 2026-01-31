from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


@dataclass
class DryRunResult:
    method: str
    url: str
    headers: dict
    body: Optional[Any] = None

    def format_output(self) -> str:
        lines = [
            "Dry run mode - no actual API call was made.",
            "",
            "Request that would be sent:",
            f"  Method:  {self.method}",
            f"  URL:     {self.url}",
            f"  Headers: {', '.join(f'{k}: {v}' for k, v in self.headers.items())}",
        ]
        if self.body:
            import json
            body_str = json.dumps(self.body, indent=4)
            lines.append(f"  Body:")
            for line in body_str.split("\n"):
                lines.append(f"    {line}")
        return "\n".join(lines)
