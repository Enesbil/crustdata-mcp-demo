from crustdata_mcp_demo.server import mcp
from crustdata_mcp_demo.client import build_request


@mcp.tool(
    name="crustdata_ping",
    annotations={
        "title": "Ping Crustdata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_ping() -> str:
    """
    Test tool to verify the MCP server is running.
    
    Returns a sample dry-run request showing what a company enrichment
    call would look like.
    """
    result = build_request(
        method="GET",
        path="/screener/company",
        params={"company_domain": "example.com"},
    )
    
    lines = [
        "Crustdata MCP Demo is running.",
        "",
        result.format_output(),
    ]
    return "\n".join(lines)
