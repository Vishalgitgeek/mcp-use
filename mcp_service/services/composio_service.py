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
        redirect_url: Optional[str] = None,
        force_reauth: bool = False
    ) -> Dict[str, Any]:
        """
        Initiate OAuth connection for an app.

        Args:
            user_id: User's ID
            app_name: App to connect (e.g., 'gmail', 'slack')
            redirect_url: URL to redirect after OAuth
            force_reauth: If True, disconnect existing connection first

        Returns:
            Dict with auth_url and connection info
        """
        try:
            # First check if already connected
            existing = self.get_connection(user_id, app_name)
            if existing:
                if force_reauth:
                    # Disconnect existing connection first
                    logger.info(f"Force reauth: disconnecting existing {app_name} for {user_id}")
                    self.disconnect(user_id, app_name)
                else:
                    logger.info(f"User {user_id} already has {app_name} connected")
                    return {
                        "auth_url": None,
                        "connection_id": existing.get("connection_id"),
                        "status": "already_connected"
                    }

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
            connections = self.client.connected_accounts.list(user_ids=user_id)
            app_lower = app_name.lower()
            app_upper = app_name.upper()

            # Get the auth_config_id for this app to match against
            auth_config_id = AUTH_CONFIG_MAP.get(app_lower)

            logger.info(f"Found {len(connections.items)} total connections for user {user_id}")

            for conn in connections.items:
                # Log connection details for debugging
                logger.info(f"Checking connection: id={conn.id}")
                logger.info(f"Connection attributes: {dir(conn)}")

                # Try multiple ways to identify the app
                conn_slug = None

                # Method 1: Check toolkit.slug
                conn_app = getattr(conn, 'toolkit', None)
                logger.info(f"  toolkit: {conn_app} (type: {type(conn_app)})")
                if conn_app:
                    if isinstance(conn_app, dict):
                        conn_slug = conn_app.get('slug', '').lower()
                    else:
                        conn_slug = getattr(conn_app, 'slug', '').lower() if hasattr(conn_app, 'slug') else None
                    logger.info(f"  toolkit slug: {conn_slug}")

                # Method 2: Check appName attribute
                if not conn_slug:
                    app_name_attr = getattr(conn, 'appName', None) or getattr(conn, 'app_name', None)
                    logger.info(f"  appName: {app_name_attr}")
                    if app_name_attr:
                        conn_slug = str(app_name_attr).lower()

                # Method 3: Check authConfigId matches our known config
                if not conn_slug and auth_config_id:
                    conn_auth_config = getattr(conn, 'authConfigId', None) or getattr(conn, 'auth_config_id', None)
                    logger.info(f"  authConfigId: {conn_auth_config} (looking for: {auth_config_id})")
                    if conn_auth_config == auth_config_id:
                        conn_slug = app_lower

                # Method 4: Check integrationId or similar
                if not conn_slug:
                    integration_id = getattr(conn, 'integrationId', None) or getattr(conn, 'integration_id', None)
                    logger.info(f"  integrationId: {integration_id}")
                    if integration_id and app_lower in str(integration_id).lower():
                        conn_slug = app_lower

                logger.info(f"Detected conn_slug: {conn_slug} for app: {app_lower}")

                if conn_slug and conn_slug == app_lower:
                    return {
                        "connection_id": conn.id,
                        "status": getattr(conn, 'status', 'active'),
                        "app": app_name
                    }

            logger.info(f"No matching connection found for {user_id}/{app_name}")
            return None

        except Exception as e:
            logger.error(f"Error checking connection for {user_id}/{app_name}: {e}")
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
                connection_id = connection["connection_id"]
                logger.info(f"Disconnecting connection {connection_id} for {app_name}")
                # Try positional argument first
                self.client.connected_accounts.delete(connection_id)
                logger.info(f"Successfully disconnected {app_name}")
                return True
            logger.warning(f"No connection found to disconnect for {user_id}/{app_name}")
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
