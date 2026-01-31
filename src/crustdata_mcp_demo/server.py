from mcp.server.fastmcp import FastMCP

from crustdata_mcp_demo.constants import SERVICE_NAME

mcp = FastMCP(SERVICE_NAME)

from crustdata_mcp_demo.tools import ping  # noqa: F401, E402
from crustdata_mcp_demo.tools import company  # noqa: F401, E402


def main():
    mcp.run()


if __name__ == "__main__":
    main()
