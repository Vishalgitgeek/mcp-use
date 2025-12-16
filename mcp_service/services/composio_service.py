"""Composio SDK service wrapper."""
import logging
import os
from typing import Optional, List, Dict, Any

from composio import Composio
from composio.exceptions import ComposioError

from ..config import COMPOSIO_API_KEY, OAUTH_REDIRECT_BASE

logger = logging.getLogger(__name__)

# Auth config IDs from your Composio account
# These are found via: c.auth_configs.list()
AUTH_CONFIG_MAP = {
    "gmail": "ac_24DkR_l4gcsg",
    "slack": "ac_EEgx5VnWdJz_",
}


class ComposioService:
    """Service for interacting with Composio SDK."""

    def __init__(self):
        """Initialize Composio client."""
        if not COMPOSIO_API_KEY:
            logger.warning("COMPOSIO_API_KEY not set - Composio features will be limited")
            self._client = None
        else:
            os.environ['COMPOSIO_API_KEY'] = COMPOSIO_API_KEY
            self._client = Composio(api_key=COMPOSIO_API_KEY)
            logger.info("Composio client initialized")

    @property
    def client(self) -> Composio:
        """Get Composio client, raising error if not initialized."""
        if self._client is None:
            raise ValueError("Composio client not initialized. Set COMPOSIO_API_KEY.")
        return self._client

    def get_available_apps(self) -> List[str]:
        """Get list of available apps/integrations."""
        return list(AUTH_CONFIG_MAP.keys())

    def _get_auth_config_id(self, app_name: str) -> str:
        """Get auth config ID for an app."""
        app_lower = app_name.lower()
        if app_lower not in AUTH_CONFIG_MAP:
            raise ValueError(f"Unsupported app: {app_name}. Supported: {list(AUTH_CONFIG_MAP.keys())}")
        return AUTH_CONFIG_MAP[app_lower]

    def initiate_connection(
        self,
        user_id: str,
        app_name: str,
        redirect_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate OAuth connection for an app.

        Args:
            user_id: User's ID
            app_name: App to connect (e.g., 'gmail', 'slack')
            redirect_url: URL to redirect after OAuth

        Returns:
            Dict with auth_url and connection info
        """
        try:
            callback_url = redirect_url or f"{OAUTH_REDIRECT_BASE}/api/integrations/callback"
            auth_config_id = self._get_auth_config_id(app_name)

            # Initiate connection with correct parameters
            connection = self.client.connected_accounts.initiate(
                user_id=user_id,
                auth_config_id=auth_config_id,
                callback_url=callback_url
            )

            return {
                "auth_url": connection.redirect_url if hasattr(connection, 'redirect_url') else str(connection),
                "connection_id": connection.id if hasattr(connection, 'id') else None,
                "status": "pending"
            }

        except ComposioError as e:
            logger.error(f"Composio error initiating connection: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initiating connection for {app_name}: {e}")
            raise

    def get_connection(self, user_id: str, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Get connection status for an app.

        Args:
            user_id: User's ID
            app_name: App name

        Returns:
            Connection info or None if not connected
        """
        try:
            connections = self.client.connected_accounts.list(user_id=user_id)
            app_lower = app_name.lower()

            for conn in connections.items:
                # Check if this connection matches the app
                conn_app = getattr(conn, 'toolkit', {})
                if isinstance(conn_app, dict):
                    conn_slug = conn_app.get('slug', '').lower()
                else:
                    conn_slug = getattr(conn_app, 'slug', '').lower() if conn_app else ''

                if conn_slug == app_lower:
                    return {
                        "connection_id": conn.id,
                        "status": getattr(conn, 'status', 'active'),
                        "app": app_name
                    }
            return None

        except Exception as e:
            logger.debug(f"No connection found for {user_id}/{app_name}: {e}")
            return None

    def get_tools(self, user_id: str, apps: List[str]) -> List[Dict[str, Any]]:
        """
        Get available tools for connected apps.

        Args:
            user_id: User's ID
            apps: List of app names

        Returns:
            List of tool definitions
        """
        try:
            tools = self.client.tools.get(
                user_id=user_id,
                toolkits=[app.upper() for app in apps]
            )

            result = []
            for tool in tools:
                tool_info = {
                    "name": getattr(tool, 'name', str(tool)),
                    "description": getattr(tool, 'description', ''),
                    "provider": apps[0] if apps else "unknown",
                    "parameters": getattr(tool, 'parameters', {})
                }
                result.append(tool_info)

            return result

        except Exception as e:
            logger.error(f"Error getting tools: {e}")
            return []

    def execute_action(
        self,
        user_id: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an action/tool.

        Args:
            user_id: User's ID
            action: Action name (e.g., 'GMAIL_SEND_EMAIL')
            params: Action parameters

        Returns:
            Execution result
        """
        try:
            result = self.client.tools.execute(
                slug=action,
                arguments=params,
                user_id=user_id,
                dangerously_skip_version_check=True
            )

            return {
                "success": True,
                "result": result
            }

        except ComposioError as e:
            logger.error(f"Composio error executing action {action}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def disconnect(self, user_id: str, app_name: str) -> bool:
        """
        Disconnect/revoke an app connection.

        Args:
            user_id: User's ID
            app_name: App to disconnect

        Returns:
            True if successful
        """
        try:
            connection = self.get_connection(user_id, app_name)
            if connection and connection.get("connection_id"):
                self.client.connected_accounts.delete(
                    id=connection["connection_id"]
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Error disconnecting {app_name}: {e}")
            return False


# Singleton instance
_composio_service: Optional[ComposioService] = None


def get_composio_service() -> ComposioService:
    """Get the singleton ComposioService instance."""
    global _composio_service
    if _composio_service is None:
        _composio_service = ComposioService()
    return _composio_service
