from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

from crustdata_mcp_demo.server import mcp
from crustdata_mcp_demo.client import build_request


class EnrichPersonInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    linkedin_urls: Optional[List[str]] = Field(
        default=None,
        description="List of LinkedIn profile URLs to enrich",
        max_length=25,
    )
    business_emails: Optional[List[str]] = Field(
        default=None,
        description="List of business email addresses to enrich",
        max_length=25,
    )
    enrich_realtime: bool = Field(
        default=False,
        description="If True, performs real-time search if data not found in database",
    )


class GetLinkedInPostsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    person_linkedin_url: Optional[str] = Field(
        default=None,
        description="LinkedIn profile URL of the person",
    )
    company_name: Optional[str] = Field(
        default=None,
        description="Name of the company",
    )
    company_domain: Optional[str] = Field(
        default=None,
        description="Domain of the company (without https://)",
    )
    company_id: Optional[int] = Field(
        default=None,
        description="Crustdata company ID",
    )
    company_linkedin_url: Optional[str] = Field(
        default=None,
        description="LinkedIn URL of the company",
    )
    fields: Optional[str] = Field(
        default=None,
        description="Comma-separated list of fields to include in response",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of posts per page (1-100)",
    )
    post_types: Optional[str] = Field(
        default=None,
        description="Comma-separated list of post types to filter",
    )
    max_reactors: int = Field(
        default=10,
        ge=0,
        description="Maximum number of reactors to include per post",
    )
    max_comments: int = Field(
        default=10,
        ge=0,
        description="Maximum number of comments to include per post",
    )


class PostProcessing(BaseModel):
    model_config = ConfigDict(extra="allow")

    strict_title_and_company_match: bool = Field(
        default=False,
        description="Enforce strict matching on title and company",
    )
    exclude_profiles: Optional[List[str]] = Field(
        default=None,
        description="LinkedIn profile URLs to exclude from results",
    )
    exclude_names: Optional[List[str]] = Field(
        default=None,
        description="Names to exclude from results",
    )


class PersonSearchFilter(BaseModel):
    model_config = ConfigDict(extra="allow")

    filter_type: str = Field(
        ...,
        description="Filter type (e.g. 'CURRENT_COMPANY', 'CURRENT_TITLE', 'SENIORITY_LEVEL', 'INDUSTRY')",
    )
    type: str = Field(
        ...,
        description="Operation type: 'in' or 'not in'",
    )
    value: Any = Field(
        ...,
        description="Filter value(s) as a list",
    )


class SearchPeopleInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filters: Optional[List[PersonSearchFilter]] = Field(
        default=None,
        description="List of search filters (combined with AND logic)",
    )
    linkedin_sales_navigator_search_url: Optional[str] = Field(
        default=None,
        description="LinkedIn Sales Navigator search URL from browser",
    )
    page: Optional[int] = Field(
        default=None,
        ge=1,
        description="Page number for pagination (use with filters, mutually exclusive with limit)",
    )
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=10000,
        description="Max results to return (sync max 25, async max 10000). Mutually exclusive with page.",
    )
    preview: bool = Field(
        default=False,
        description="Get preview of profiles (cannot be used with page)",
    )
    background_job: bool = Field(
        default=False,
        description="Run search asynchronously for large result sets (required when limit > 25)",
    )
    job_id: Optional[str] = Field(
        default=None,
        description="Job ID to check status of a background job",
    )
    post_processing: Optional[PostProcessing] = Field(
        default=None,
        description="Extra rules applied after search completes",
    )


@mcp.tool(
    name="crustdata_enrich_person",
    annotations={
        "title": "Enrich Person",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_enrich_person(params: EnrichPersonInput) -> str:
    """
    Enrich person data using LinkedIn URLs or business email addresses.
    
    Retrieves comprehensive info including employment history, education,
    skills, connections, and more.
    
    Provide at least one: linkedin_urls or business_emails.
    
    Args:
        params: EnrichPersonInput containing:
            - linkedin_urls: List of LinkedIn profile URLs
            - business_emails: List of business email addresses
            - enrich_realtime: If True, search web in real-time if not in database
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Note: If a profile isn't found, Crustdata auto-enriches it within 30-60 min.
    """
    query_params = {}
    
    if params.linkedin_urls:
        query_params["linkedin_profile_url"] = ",".join(params.linkedin_urls)
    
    if params.business_emails:
        query_params["business_email"] = ",".join(params.business_emails)
    
    if params.enrich_realtime:
        query_params["enrich_realtime"] = "true"
    
    result = build_request(
        method="GET",
        path="/screener/person/enrich",
        params=query_params,
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_get_linkedin_posts",
    annotations={
        "title": "Get LinkedIn Posts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_get_linkedin_posts(params: GetLinkedInPostsInput) -> str:
    """
    Get recent LinkedIn posts and engagement metrics for a person or company.
    
    Returns posts with content, reactions, comments, shares, and detailed
    info about people who interacted with the posts.
    
    Provide at least one: person_linkedin_url, company_name, company_domain,
    company_id, or company_linkedin_url.
    
    Args:
        params: GetLinkedInPostsInput containing:
            - person_linkedin_url: LinkedIn profile URL of a person
            - company_name: Name of company
            - company_domain: Domain of company (without https://)
            - company_id: Crustdata company ID
            - company_linkedin_url: LinkedIn URL of company
            - fields: Comma-separated fields to include
            - page: Page number (default 1)
            - limit: Posts per page (1-100, default 10)
            - post_types: Filter by post types
            - max_reactors: Max reactors per post (default 10)
            - max_comments: Max comments per post (default 10)
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Note: Data is fetched in real-time. Expect 30-60 second latency.
    """
    query_params = {}
    
    if params.person_linkedin_url:
        query_params["person_linkedin_url"] = params.person_linkedin_url
    
    if params.company_name:
        query_params["company_name"] = params.company_name
    
    if params.company_domain:
        query_params["company_domain"] = params.company_domain
    
    if params.company_id:
        query_params["company_id"] = params.company_id
    
    if params.company_linkedin_url:
        query_params["company_linkedin_url"] = params.company_linkedin_url
    
    if params.fields:
        query_params["fields"] = params.fields
    
    query_params["page"] = params.page
    query_params["limit"] = params.limit
    
    if params.post_types:
        query_params["post_types"] = params.post_types
    
    query_params["max_reactors"] = params.max_reactors
    query_params["max_comments"] = params.max_comments
    
    result = build_request(
        method="GET",
        path="/screener/linkedin_posts",
        params=query_params,
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_search_people",
    annotations={
        "title": "Search People",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_search_people(params: SearchPeopleInput) -> str:
    """
    Search for professional profiles using filters or Sales Navigator URL.
    
    Find people by company, title, seniority, industry, location, skills, etc.
    Supports both filter-based search and LinkedIn Sales Navigator URL import.
    
    Args:
        params: SearchPeopleInput containing:
            - filters: List of filter objects with filter_type, type, value
            - linkedin_sales_navigator_search_url: Import search from Sales Navigator
            - page: Page number (use with filters, mutually exclusive with limit)
            - limit: Max results (sync max 25, async max 10000)
            - preview: Get preview of profiles
            - background_job: Run async for large result sets (required when limit > 25)
            - job_id: Check status of background job
            - post_processing: Extra rules (exclude profiles/names, strict matching)
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Filter types:
        CURRENT_COMPANY, CURRENT_TITLE, PAST_TITLE, PAST_COMPANY
        SENIORITY_LEVEL: ['Owner / Partner', 'CXO', 'Vice President', 'Director', etc.]
        INDUSTRY, REGION, COMPANY_HEADCOUNT
        YEARS_AT_CURRENT_COMPANY, YEARS_OF_EXPERIENCE
        FUNCTION, KEYWORD, COMPANY_TYPE
    
    Boolean filters (just filter_type, no value):
        POSTED_ON_SOCIAL_MEDIA, RECENTLY_CHANGED_JOBS, IN_THE_NEWS
    """
    body = {}
    
    if params.filters:
        body["filters"] = [f.model_dump(exclude_none=True) for f in params.filters]
    
    if params.linkedin_sales_navigator_search_url:
        body["linkedin_sales_navigator_search_url"] = params.linkedin_sales_navigator_search_url
    
    if params.page is not None:
        body["page"] = params.page
    
    if params.limit is not None:
        body["limit"] = params.limit
    
    if params.preview:
        body["preview"] = params.preview
    
    if params.background_job:
        body["background_job"] = params.background_job
    
    if params.job_id:
        body["job_id"] = params.job_id
    
    if params.post_processing:
        body["post_processing"] = params.post_processing.model_dump(exclude_none=True)
    
    result = build_request(
        method="POST",
        path="/screener/person/search",
        json_body=body,
    )
    
    return result.format_output()
