from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(location:str) -> str:
    """Get the weather location."""
    return "The weather in Bangalore is sunny."

if __name__ == '__main__':
    mcp.run(transport="streamable-http")
    #The transport="streamable-http" argument tells the server to:
    #- use the Streamable HTTP transport to recieve and respond to tool function calls.
    #- This is useful for web-based clients that can handle HTTP requests and responses.