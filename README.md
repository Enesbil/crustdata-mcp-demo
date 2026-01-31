# Crustdata MCP Demo

A proof-of-concept MCP server for the Crustdata API. This exposes all of Crustdata's company, people, and web APIs as tools that AI assistants can discover and call.

## Quick note

This runs in dry-run mode since I don't have API access yet. When you call a tool, it shows you exactly what request would be sent to the Crustdata API. The structure is all there, just swap in real HTTP calls when you have credentials.

## Tools

### Company APIs
- **crustdata_enrich_company** - Enrich companies by domain, name, LinkedIn URL, or ID
- **crustdata_screen_companies** - Filter companies by headcount, funding, location, skills, etc.
- **crustdata_search_companies** - Real-time company search with structured filters
- **crustdata_get_company_people** - Get employees and decision makers at a company

### People APIs
- **crustdata_enrich_person** - Enrich LinkedIn profiles or business emails
- **crustdata_search_people** - Find people by company, title, seniority, industry, etc.
- **crustdata_get_linkedin_posts** - Get LinkedIn posts and engagement metrics

### Web APIs
- **crustdata_web_search** - SERP search with geolocation and source filtering
- **crustdata_web_fetch** - Fetch HTML content from URLs

### Utility
- **crustdata_ping** - Test that the server is running

## Setup

```bash
cd crustDataMCP
pip install -e .
```

## Running

```bash
python -m crustdata_mcp_demo.server
```

Or use the runner script:

```bash
python run_server.py
```

## Using with Cursor

Add to your MCP config (`.cursor/mcp.json` in your project or global Cursor settings):

```json
{
  "mcpServers": {
    "crustdata": {
      "command": "python",
      "args": ["c:\\Users\\Admin\\Desktop\\dev\\projects\\crustDataMCP\\run_server.py"]
    }
  }
}
```

Restart Cursor after adding the config.

## Test Prompts

Once the MCP server is connected, try these prompts with your AI:

### Basic test
> "Use the crustdata ping tool to check if the server is working"

### Company enrichment
> "Get company info for hubspot.com and stripe.com using crustdata"

> "Look up OpenAI's headcount and job openings with crustdata"

### Company screening
> "Use crustdata to find companies with over 500 employees headquartered in the USA"

> "Find startups founded after 2020 with more than $5M in funding using crustdata"

### Company search
> "Search for Fortune 500 companies in the Technology industry using crustdata"

### Company people
> "Get the employees and decision makers at Hubspot using crustdata"

### Person enrichment
> "Look up the LinkedIn profile for https://www.linkedin.com/in/satyanadella/ using crustdata"

> "Enrich the email ceo@example.com using crustdata"

### People search
> "Find VPs and Directors at Google in the Engineering function using crustdata"

> "Search for people who recently changed jobs at Microsoft using crustdata"

### LinkedIn posts
> "Get recent LinkedIn posts from Hubspot's company page using crustdata"

### Web search
> "Search the web for 'B2B data enrichment API' using crustdata"

> "Search news articles about AI startups using crustdata"

### Web fetch
> "Fetch the HTML content of https://www.crustdata.com using crustdata"

## Project Structure

```
src/crustdata_mcp_demo/
├── server.py       # FastMCP server + entry point
├── client.py       # Dry-run request builder
├── models.py       # Shared Pydantic models
├── constants.py    # API base URL, service name
└── tools/
    ├── ping.py     # Test tool
    ├── company.py  # Company enrichment, screening, search, people
    ├── people.py   # Person enrichment, search, LinkedIn posts
    └── web.py      # Web search and fetch
```

## API Coverage

This covers all endpoints from the Crustdata API:
- `GET /screener/company` - Company enrichment
- `POST /screener/screen/` - Company screening
- `POST /screener/company/search` - Company search
- `GET /screener/company/people` - Company people
- `GET /screener/person/enrich` - Person enrichment
- `POST /screener/person/search` - People search
- `GET /screener/linkedin_posts` - LinkedIn posts
- `POST /screener/web-search` - Web search
- `POST /screener/web-fetch` - Web fetch
