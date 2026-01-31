from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

from crustdata_mcp_demo.server import mcp
from crustdata_mcp_demo.client import build_request


class EnrichCompanyInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    company_domains: List[str] = Field(
        ...,
        description="List of company website domains to enrich (e.g. ['hubspot.com', 'google.com'])",
        min_length=1,
        max_length=25,
    )
    fields: Optional[List[str]] = Field(
        default=None,
        description="Specific fields to retrieve (e.g. ['company_name', 'headcount.headcount']). If not specified, returns all top-level non-object fields.",
    )
    enrich_realtime: bool = Field(
        default=False,
        description="If True, will enrich companies not in database within 10 minutes",
    )


class ScreeningCondition(BaseModel):
    model_config = ConfigDict(extra="allow")

    column: str = Field(..., description="Column name to filter on (e.g. 'headcount', 'total_investment_usd')")
    type: str = Field(..., description="Comparison type: '=' for equals, '=>' for gte, '<=' for lte, '(.)' for contains")
    value: Any = Field(..., description="Value to compare against")
    allow_null: bool = Field(default=False, description="Whether to include null values")


class ScreenCompaniesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    op: str = Field(
        default="and",
        description="Logical operator to combine conditions: 'and' or 'or'",
    )
    conditions: List[ScreeningCondition] = Field(
        ...,
        description="List of filter conditions",
        min_length=1,
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    count: int = Field(default=100, ge=1, le=1000, description="Number of results to return")
    sorts: Optional[List[dict]] = Field(default=None, description="Optional sorting criteria")


class CompanySearchFilter(BaseModel):
    model_config = ConfigDict(extra="allow")

    filter_type: str = Field(..., description="Filter type (e.g. 'COMPANY_HEADCOUNT', 'REGION', 'INDUSTRY', 'ANNUAL_REVENUE')")
    type: str = Field(..., description="Operation type: 'in', 'not in', or 'between'")
    value: Any = Field(..., description="Filter value(s)")
    sub_filter: Optional[str] = Field(default=None, description="Sub-filter for certain types (e.g. 'USD' for ANNUAL_REVENUE)")


class SearchCompaniesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filters: List[CompanySearchFilter] = Field(
        ...,
        description="List of search filters (combined with AND logic)",
        min_length=1,
    )
    page: int = Field(default=1, ge=1, description="Page number for pagination (25 results per page)")


@mcp.tool(
    name="crustdata_enrich_company",
    annotations={
        "title": "Enrich Company",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_enrich_company(params: EnrichCompanyInput) -> str:
    """
    Enrich company data by domain.
    
    Retrieves detailed information about one or more companies including
    headcount metrics, funding, reviews, web traffic, job openings, news, etc.
    
    Args:
        params: EnrichCompanyInput containing:
            - company_domains: List of domains like ['hubspot.com', 'google.com']
            - fields: Optional list of specific fields to retrieve
            - enrich_realtime: Set True to enrich unknown companies (takes ~10 min)
    
    Returns:
        Dry-run output showing the request that would be sent to Crustdata API.
    
    Example domains: 'hubspot.com', 'stripe.com', 'openai.com'
    Example fields: 'company_name', 'headcount.headcount', 'job_openings', 'news_articles'
    """
    query_params = {
        "company_domain": ",".join(params.company_domains),
    }
    
    if params.fields:
        query_params["fields"] = ",".join(params.fields)
    
    if params.enrich_realtime:
        query_params["enrich_realtime"] = "True"
    
    result = build_request(
        method="GET",
        path="/screener/company",
        params=query_params,
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_screen_companies",
    annotations={
        "title": "Screen Companies",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_screen_companies(params: ScreenCompaniesInput) -> str:
    """
    Screen and filter companies based on growth and firmographic criteria.
    
    Use this for complex queries with conditions on columns like headcount,
    funding, location, employee skills, etc.
    
    Args:
        params: ScreenCompaniesInput containing:
            - op: 'and' or 'or' to combine conditions
            - conditions: List of filter conditions with column, type, value
            - offset: Pagination offset
            - count: Number of results (max 1000)
            - sorts: Optional sorting
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Condition types:
        '=' : equals
        '=>': greater than or equal
        '<=': less than or equal
        '(.)': contains (for text/array fields)
    
    Example columns:
        'headcount', 'total_investment_usd', 'largest_headcount_country',
        'company_website_domain', 'employee_skills_31_to_50_pct'
    """
    body = {
        "filters": {
            "op": params.op,
            "conditions": [c.model_dump() for c in params.conditions],
        },
        "hidden_columns": [],
        "offset": params.offset,
        "count": params.count,
        "sorts": params.sorts or [],
    }
    
    result = build_request(
        method="POST",
        path="/screener/screen/",
        json_body=body,
    )
    
    return result.format_output()


@mcp.tool(
    name="crustdata_search_companies",
    annotations={
        "title": "Search Companies",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def crustdata_search_companies(params: SearchCompaniesInput) -> str:
    """
    Search for companies using structured filters.
    
    This uses a different filter format than screening. Filters are combined
    with AND logic. Returns 25 results per page.
    
    Args:
        params: SearchCompaniesInput containing:
            - filters: List of filter objects with filter_type, type, value
            - page: Page number (starts at 1)
    
    Returns:
        Dry-run output showing the request that would be sent.
    
    Filter types and values:
        COMPANY_HEADCOUNT: ['1-10', '11-50', '51-200', '201-500', '501-1,000', '1,001-5,000', '5,001-10,000', '10,001+']
        REGION: Use region names like 'United States', 'Europe'
        INDUSTRY: Industry names
        ANNUAL_REVENUE: Use 'between' with {min, max} and sub_filter='USD'
        ACCOUNT_ACTIVITIES: ['Senior leadership changes in last 3 months', 'Funding events in past 12 months']
        FORTUNE: ['Fortune 50', 'Fortune 51-100', 'Fortune 101-250', 'Fortune 251-500']
        JOB_OPPORTUNITIES: ['Hiring']
    """
    body = {
        "filters": [f.model_dump(exclude_none=True) for f in params.filters],
        "page": params.page,
    }
    
    result = build_request(
        method="POST",
        path="/screener/company/search",
        json_body=body,
    )
    
    return result.format_output()
