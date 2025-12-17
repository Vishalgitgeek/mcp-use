"""
OpenAI GPT-4 Agent for testing MCP Integration Service.

This agent uses natural language to decide which tools to execute
via the MCP Integration Service APIs.

Usage:
    python -m tests.agent --user-id <USER_ID>
"""
import os
import json
import argparse
import requests
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class MCPAgentClient:
    """Client for interacting with MCP Integration Service APIs."""

    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base.rstrip("/")
        self.headers = {"X-API-Key": api_key}

    def health_check(self) -> bool:
        """Check if the service is healthy."""
        try:
            resp = requests.get(f"{self.api_base}/api/tools/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def get_user_tools(self, user_id: str) -> list:
        """Get available tools for a user."""
        resp = requests.get(
            f"{self.api_base}/api/tools",
            params={"user_id": user_id},
            headers=self.headers,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json().get("tools", [])

    def get_provider_actions(self, provider: str) -> list:
        """Get available actions for a provider."""
        resp = requests.get(
            f"{self.api_base}/api/tools/actions/{provider}",
            headers=self.headers,
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get("actions", [])

    def execute_tool(self, user_id: str, action: str, params: dict) -> dict:
        """Execute a tool action."""
        resp = requests.post(
            f"{self.api_base}/api/tools/execute",
            headers={**self.headers, "Content-Type": "application/json"},
            json={
                "user_id": user_id,
                "action": action,
                "params": params
            },
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()


class MCPAgent:
    """OpenAI GPT-4 Agent that uses MCP tools via natural language."""

    def __init__(self, user_id: str, client: MCPAgentClient):
        self.user_id = user_id
        self.client = client
        self.openai = OpenAI(api_key=OPENAI_API_KEY)
        self.conversation_history = []
        self.available_tools = []

    def _build_openai_tools(self) -> list:
        """Build OpenAI function definitions from available provider actions."""
        tools = []

        # Get actions for supported providers
        for provider in ["gmail", "slack"]:
            try:
                actions = self.client.get_provider_actions(provider)
                for action in actions:
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": action["name"],
                            "description": action["description"],
                            "parameters": self._get_action_parameters(action["name"])
                        }
                    }
                    tools.append(tool_def)
            except Exception as e:
                print(f"Warning: Could not get actions for {provider}: {e}")

        return tools

    def _get_action_parameters(self, action_name: str) -> dict:
        """Get parameter schema for an action."""
        # Define parameter schemas for known actions
        schemas = {
            "GMAIL_SEND_EMAIL": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"}
                },
                "required": ["to", "subject", "body"]
            },
            "GMAIL_LIST_EMAILS": {
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "description": "Maximum number of emails to return", "default": 10},
                    "query": {"type": "string", "description": "Search query"}
                }
            },
            "GMAIL_GET_EMAIL": {
                "type": "object",
                "properties": {
                    "email_id": {"type": "string", "description": "Email ID to retrieve"}
                },
                "required": ["email_id"]
            },
            "GMAIL_SEARCH_EMAILS": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": ["query"]
            },
            "GMAIL_CREATE_DRAFT": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"}
                },
                "required": ["to", "subject", "body"]
            },
            "SLACK_SEND_MESSAGE": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel name or ID"},
                    "text": {"type": "string", "description": "Message text"}
                },
                "required": ["channel", "text"]
            },
            "SLACK_LIST_CHANNELS": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max channels to return", "default": 100}
                }
            },
            "SLACK_GET_CHANNEL_HISTORY": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel ID"},
                    "limit": {"type": "integer", "description": "Number of messages", "default": 20}
                },
                "required": ["channel"]
            },
            "SLACK_UPLOAD_FILE": {
                "type": "object",
                "properties": {
                    "channels": {"type": "string", "description": "Channel to upload to"},
                    "content": {"type": "string", "description": "File content"},
                    "filename": {"type": "string", "description": "Filename"}
                },
                "required": ["channels", "content", "filename"]
            }
        }

        return schemas.get(action_name, {"type": "object", "properties": {}})

    def _execute_function_call(self, function_name: str, arguments: dict) -> str:
        """Execute a function call via the MCP API."""
        print(f"\n  Executing: {function_name}")
        print(f"  Arguments: {json.dumps(arguments, indent=2)}")

        try:
            result = self.client.execute_tool(
                user_id=self.user_id,
                action=function_name,
                params=arguments
            )

            if result.get("success"):
                return json.dumps(result.get("result", {}), indent=2)
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"Execution failed: {str(e)}"

    def chat(self, user_message: str) -> str:
        """Process a user message and return agent response."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build tools list
        tools = self._build_openai_tools()

        # System prompt
        system_prompt = f"""You are an AI assistant that helps users interact with their connected integrations (Gmail, Slack).
You have access to tools that can:
- Send emails via Gmail
- Read and search emails
- Send Slack messages
- List Slack channels

The user ID is: {self.user_id}

When the user asks you to perform an action, use the appropriate tool.
Be helpful and confirm what action you're about to take before executing.
If a tool execution fails, explain what went wrong."""

        # Call OpenAI
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None
        )

        assistant_message = response.choices[0].message

        # Check if the model wants to call a function
        if assistant_message.tool_calls:
            # Execute each tool call
            tool_results = []
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                result = self._execute_function_call(function_name, arguments)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": result
                })

            # Add assistant message and tool results to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            for tool_result in tool_results:
                self.conversation_history.append(tool_result)

            # Get follow-up response from model
            follow_up = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": system_prompt}] + self.conversation_history
            )

            final_response = follow_up.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })

            return final_response

        else:
            # No function call, just return the response
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content
            })
            return assistant_message.content


def main():
    parser = argparse.ArgumentParser(description="MCP Integration Agent")
    parser.add_argument("--user-id", required=True, help="User ID to act on behalf of")
    args = parser.parse_args()

    # Validate configuration
    if not AGENT_API_KEY:
        print("Error: AGENT_API_KEY not set in environment")
        return

    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set in environment")
        return

    # Create client and check health
    client = MCPAgentClient(API_BASE_URL, AGENT_API_KEY)

    print(f"MCP Integration Agent")
    print(f"API Base: {API_BASE_URL}")
    print(f"User ID: {args.user_id}")
    print("-" * 50)

    if not client.health_check():
        print("Warning: Service health check failed. Is the server running?")

    # Create agent
    agent = MCPAgent(args.user_id, client)

    print("\nAgent ready! Type your requests (or 'quit' to exit)")
    print("Examples:")
    print("  - 'Send an email to test@example.com saying hello'")
    print("  - 'List my recent emails'")
    print("  - 'Send a message to #general on Slack'")
    print("-" * 50)

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            print("\nAgent: ", end="")
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
