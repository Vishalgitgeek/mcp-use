"""Service for executing MCPAgent queries."""
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from auth import get_credentials_for_user
from mcp_config import build_mcp_config
from config import OPENAI_MODEL, MCP_AGENT_MAX_STEPS


async def execute_agent_query(email: str, query: str) -> str:
    """
    Execute a query using MCPAgent with the specified user's credentials.
    
    Args:
        email: User email address
        query: Natural language query to execute
        
    Returns:
        Result of the agent execution
        
    Raises:
        ValueError: If user credentials not found
        Exception: If agent execution fails
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get credentials for user
        credentials = get_credentials_for_user(email)
        logger.info(f"Retrieved credentials for user: {email}")
        
        # Build MCP configuration
        # Start with filesystem only - Google Drive MCP server is problematic
        mcp_config = build_mcp_config(credentials, include_gdrive=False)
        logger.info(f"MCP config created with {len(mcp_config['mcpServers'])} servers: {list(mcp_config['mcpServers'].keys())}")
        
        # Create MCP client with error handling
        try:
            client = MCPClient(mcp_config)
            logger.info("MCP client created successfully")
        except Exception as e:
            logger.error(f"Failed to create MCP client: {str(e)}")
            raise Exception(f"MCP client initialization failed: {str(e)}. Make sure Node.js and npx are installed and MCP servers can start.")
        
        # Create agent
        llm = ChatOpenAI(model=OPENAI_MODEL)
        agent = MCPAgent(llm=llm, client=client, max_steps=MCP_AGENT_MAX_STEPS)
        logger.info("MCP agent created successfully")
        
        # Execute query
        logger.info(f"Executing query: {query[:50]}...")
        result = await agent.run(query)
        logger.info("Query executed successfully")
        
        return str(result)
        
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Agent execution error: {str(e)}")
        error_msg = str(e)
        if "Connection closed" in error_msg:
            raise Exception(
                "MCP server connection failed. This usually means:\n"
                "1. Node.js/npx is not installed or not in PATH\n"
                "2. MCP servers failed to start\n"
                "3. Google Drive MCP server configuration issue\n\n"
                f"Original error: {error_msg}"
            )
        raise

