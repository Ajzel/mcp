from mcp.server.fastmcp import FastMCP

mcp = FastMCP("math")

@mcp.tool()
def add(a:int, b:int) -> int:
    return a + b

@mcp.tool()
def multiply(a:int, b:int) -> int:
    return a * b

#The transport="stdio" argument tells the server to:
 #   - use the standard input and output (stdin and stdout) to recieve and respond to tool function calls.
    

if __name__ == "__main__":
    mcp.run(transport="stdio")
    
    
