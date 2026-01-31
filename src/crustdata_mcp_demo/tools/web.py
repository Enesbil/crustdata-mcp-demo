from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from crustdata_mcp_demo.server import mcp
from crustdata_mcp_demo.client import build_request


class WebSearchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(
        ...,
        description="Search query text",
        min_length=1,
        max_length=1000,
    )
    geolocation: Optional[str] = Field(
        default=None,
        description="ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB', 'DE')",
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="Search sources: 'news', 'web', 'scholar-articles', 'scholar-articles-enriched', 'scholar-author'",
    )
    site: Optional[str] = Field(
        default=None,
        description="Restrict results to a specific domain (e.g. 'github.com')",
    )
    start_date: Optional[int] = Field(
        default=None,
        description="Unix timestamp for start date filter",
    )
    end_date: Optional[int] = Field(
        default=None,
        description="Unix timestamp for end date filter",
    )
    fetch_content: bool = Field(
        default=False,
        description="If True, fetches full HTML content for each result URL",
    )


class WebFetchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    urls: List[str] = Field(
        ...,
        description="List of URLs to fetch (must include http:// or https://)",
        min_length=1,
        max_length=10,
    )


@mcp.tool(
    name="crustdata_web_search",
    annotations={
        "title": "Web Search",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_web_search(params: WebSearchInput) -> str:
    """
    Perform a web search using Crustdata's SERP API.
    
    Returns search results with titles, URLs, snippets, and positions.
    Useful for competitive intelligence, market research, lead generation.
    
    Args:
        params: WebSearchInput containing:
            - query: Search query text (required)
            - geolocation: Country code for localized results (e.g. 'US', 'GB')
            - sources: List of sources to search ('news', 'web', 'scholar-articles', etc)
            - site: Restrict to a specific domain
            - start_date/end_date: Unix timestamps for date filtering
            - fetch_content: If True, also fetches HTML content for each result
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Rate limit: 15 requests per minute
    Results: Typically 5-15 per search, no pagination
    """
    body = {"query": params.query}
    
    if params.geolocation:
        body["geolocation"] = params.geolocation
    
    if params.sources:
        body["sources"] = params.sources
    
    if params.site:
        body["site"] = params.site
    
    if params.start_date:
        body["startDate"] = params.start_date
    
    if params.end_date:
        body["endDate"] = params.end_date
    
    query_params = None
    if params.fetch_content:
        query_params = {"fetch_content": "true"}
    
    result = build_request(
        method="POST",
        path="/screener/web-search",
        params=query_params,
        json_body=body,
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_web_fetch",
    annotations={
        "title": "Web Fetch",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_web_fetch(params: WebFetchInput) -> str:
    """
    Fetch HTML content from one or more URLs.
    
    Returns the page title and full HTML content for each URL.
    Useful for content extraction, web scraping, SEO analysis.
    
    Args:
        params: WebFetchInput containing:
            - urls: List of URLs to fetch (max 10, must include protocol)
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Notes:
        - URLs must start with http:// or https://
        - Max 10 URLs per request
        - Only fetches publicly accessible pages (no auth)
        - Most pages fetched in 2-5 seconds
    """
    result = build_request(
        method="POST",
        path="/screener/web-fetch",
        json_body={"urls": params.urls},
    )
    
    return result.format_output()
