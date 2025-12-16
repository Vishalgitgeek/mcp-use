import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient


async def main():
    load_dotenv()

    os.environ["SUPABASE_ACCESS_TOKEN"] = os.getenv("SUPABASE_ACCESS_TOKEN", "")

    

    # client = MCPClient(config)
    client = MCPClient.from_config_file("mcp_multi.json")

    llm = ChatOpenAI(model='gpt-4o')

    agent = MCPAgent(llm = llm, client=client, max_steps=30)
    query = input("what are you thinking ?? : ")
    result = await agent.run(query)

    print(f"\nResult : {result}") 


if __name__=="__main__":
    asyncio.run(main())