"""Integration service combining MongoDB and Composio operations."""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..db.mongodb import get_collection
from ..models.integration import Integration, IntegrationStatus
from .composio_service import get_composio_service

logger = logging.getLogger(__name__)


class IntegrationService:
    """Service for managing user integrations."""

    def __init__(self):
        """Initialize integration service."""
        self.composio = get_composio_service()

    async def get_user_integrations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all integrations for a user.

        Args:
            user_id: User ID

        Returns:
            List of integration records
        """
        collection = await get_collection("integrations")
        cursor = collection.find({"user_id": user_id})
        integrations = await cursor.to_list(length=100)

        return [
            {
                "provider": i["provider"],
                "status": i["status"],
                "connected_email": i.get("connected_email"),
                "connected_at": i.get("created_at")
            }
            for i in integrations
        ]

    async def get_integration(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific integration for a user.

        Args:
            user_id: User ID
            provider: Integration provider name

        Returns:
            Integration record or None
        """
        collection = await get_collection("integrations")
        integration = await collection.find_one({
            "user_id": user_id,
            "provider": provider.lower()
        })
        return integration

    async def initiate_connection(
        self,
        user_id: str,
        provider: str,
        redirect_url: Optional[str] = None,
        force_reauth: bool = False
    ) -> Dict[str, Any]:
        """
        Start OAuth connection flow for an integration.

        Args:
            user_id: User ID
            provider: Integration provider (gmail, slack, etc.)
            redirect_url: Optional custom redirect URL
            force_reauth: If True, disconnect and re-authenticate even if already connected

        Returns:
            Dict with auth_url for OAuth redirect
        """
        provider = provider.lower()

        # Check if already connected in MongoDB
        existing = await self.get_integration(user_id, provider)
        if existing and existing.get("status") == IntegrationStatus.ACTIVE.value and not force_reauth:
            raise ValueError(f"User already has an active {provider} connection")

        # If force_reauth, remove existing MongoDB record
        if force_reauth and existing:
            collection = await get_collection("integrations")
            await collection.delete_one({"_id": existing["_id"]})
            existing = None
            logger.info(f"Force reauth: removed existing MongoDB record for {provider}")

        # Create entity_id from user_id
        entity_id = f"user_{user_id}"

        # Initiate connection with Composio
        connection_info = self.composio.initiate_connection(
            user_id=entity_id,
            app_name=provider,
            redirect_url=redirect_url,
            force_reauth=force_reauth
        )

        logger.info(f"Composio returned: {connection_info}")

        # Handle already connected case
        if connection_info.get("status") == "already_connected":
            logger.info(f"Handling already_connected case for {provider}")
            # Update MongoDB to reflect the active connection
            collection = await get_collection("integrations")
            integration_data = {
                "user_id": user_id,
                "provider": provider,
                "composio_entity_id": entity_id,
                "composio_connection_id": connection_info.get("connection_id"),
                "status": IntegrationStatus.ACTIVE.value,
                "updated_at": datetime.utcnow()
            }

            if existing:
                await collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": integration_data}
                )
            else:
                integration_data["created_at"] = datetime.utcnow()
                await collection.insert_one(integration_data)

            return {
                "auth_url": None,
                "status": "already_connected",
                "provider": provider
            }

        # Create or update integration record for pending connection
        collection = await get_collection("integrations")

        integration_data = {
            "user_id": user_id,
            "provider": provider,
            "composio_entity_id": entity_id,
            "composio_connection_id": connection_info.get("connection_id"),
            "status": IntegrationStatus.PENDING.value,
            "updated_at": datetime.utcnow()
        }

        if existing:
            await collection.update_one(
                {"_id": existing["_id"]},
                {"$set": integration_data}
            )
        else:
            integration_data["created_at"] = datetime.utcnow()
            await collection.insert_one(integration_data)

        return {
            "auth_url": connection_info["auth_url"],
            "provider": provider
        }

    async def complete_connection(
        self,
        user_id: str,
        provider: str,
        connected_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark a connection as complete after OAuth callback.

        Args:
            user_id: User ID
            provider: Integration provider
            connected_email: Email of the connected account

        Returns:
            Updated integration info
        """
        collection = await get_collection("integrations")
        provider = provider.lower()
        entity_id = f"user_{user_id}"

        # Use upsert to create or update the record
        result = await collection.update_one(
            {"user_id": user_id, "provider": provider},
            {
                "$set": {
                    "status": IntegrationStatus.ACTIVE.value,
                    "connected_email": connected_email,
                    "updated_at": datetime.utcnow(),
                    "composio_entity_id": entity_id
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "provider": provider,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        logger.info(f"Complete connection: matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_id}")

        return {
            "provider": provider,
            "status": "active",
            "connected_email": connected_email
        }

    async def disconnect(self, user_id: str, provider: str) -> bool:
        """
        Disconnect an integration.

        Args:
            user_id: User ID
            provider: Integration provider

        Returns:
            True if successfully disconnected
        """
        provider = provider.lower()

        # Get the integration record
        integration = await self.get_integration(user_id, provider)
        if not integration:
            return False

        entity_id = integration.get("composio_entity_id", f"user_{user_id}")

        # Disconnect from Composio
        try:
            self.composio.disconnect(entity_id, provider)
        except Exception as e:
            logger.warning(f"Error disconnecting from Composio: {e}")

        # Remove from database
        collection = await get_collection("integrations")
        result = await collection.delete_one({
            "user_id": user_id,
            "provider": provider
        })

        return result.deleted_count > 0

    async def get_user_tools(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all available tools for a user based on their connected integrations.

        Args:
            user_id: User ID

        Returns:
            List of available tools
        """
        # Get user's active integrations
        integrations = await self.get_user_integrations(user_id)
        active_providers = [
            i["provider"] for i in integrations
            if i["status"] == IntegrationStatus.ACTIVE.value
        ]

        if not active_providers:
            return []

        entity_id = f"user_{user_id}"

        # Get tools from Composio
        return self.composio.get_tools(entity_id, active_providers)

    async def execute_tool(
        self,
        user_id: str,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool/action for a user.

        Args:
            user_id: User ID
            action: Action to execute (e.g., 'GMAIL_SEND_EMAIL')
            params: Action parameters

        Returns:
            Execution result
        """
        # Extract provider from action name (e.g., GMAIL_SEND_EMAIL -> gmail)
        provider = action.split("_")[0].lower()

        # Verify user has this integration connected
        integration = await self.get_integration(user_id, provider)
        if not integration:
            return {
                "success": False,
                "error": f"User does not have {provider} connected"
            }

        if integration.get("status") != IntegrationStatus.ACTIVE.value:
            return {
                "success": False,
                "error": f"{provider} integration is not active"
            }

        entity_id = integration.get("composio_entity_id", f"user_{user_id}")

        # Execute via Composio
        return self.composio.execute_action(entity_id, action, params)


# Singleton instance
_integration_service: Optional[IntegrationService] = None


def get_integration_service() -> IntegrationService:
    """Get the singleton IntegrationService instance."""
    global _integration_service
    if _integration_service is None:
        _integration_service = IntegrationService()
    return _integration_service
