import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("BankDataServer")

DATA_FILE = Path(__file__).parent / "mock_bank_data.json"


@mcp.tool()
def get_client_data() -> str:
    """
    Opens mock_bank_data.json, reads its contents, and returns the raw
    JSON data as a string. Use this tool whenever you need client/bank
    records to perform compliance or risk analysis.
    """
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return json.dumps(data)


if __name__ == "__main__":
    # Runs the server over stdio so ADK (or any MCP client) can connect
    mcp.run(transport="stdio")