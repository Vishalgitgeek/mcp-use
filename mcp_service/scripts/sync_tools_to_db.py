"""
Sync Tools to MongoDB

This script reads the tools configuration from tools_config.py
and stores/updates the tool definitions in MongoDB.

Usage:
    python -m mcp_service.scripts.sync_tools_to_db

This script:
1. Reads ENABLED_TOOLS from tools_config.py
2. Stores/updates tool configuration in MongoDB
3. Marks disabled tools as inactive
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict

from motor.motor_asyncio import AsyncIOMotorClient
from ..config import MONGODB_URI, MONGODB_DB_NAME
from ..tools_config import get_enabled_tools, get_tool_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def sync_tools_to_mongodb():
    """
    Sync tool configuration to MongoDB.
    
    This function:
    - Connects to MongoDB
    - Creates/updates 'tools' collection with enabled tools
    - Stores tool metadata and auth_config_ids
    """
    logger.info("Starting tool synchronization to MongoDB...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        tools_collection = db["tools"]
        
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {MONGODB_URI}")
        
        # Get enabled tools from config
        enabled_tools = get_enabled_tools()
        logger.info(f"Found {len(enabled_tools)} enabled tools in configuration")
        
        # Track synced tools
        synced_count = 0
        updated_count = 0
        
        # Sync each tool
        for app_name, auth_config_id in enabled_tools.items():
            metadata = get_tool_metadata(app_name)
            
            tool_doc = {
                "app_name": app_name,
                "auth_config_id": auth_config_id,
                "enabled": metadata.get("enabled", True),
                "category": metadata.get("category", "uncategorized"),
                "description": metadata.get("description", ""),
                "updated_at": datetime.utcnow(),
            }
            
            # Check if tool exists
            existing = await tools_collection.find_one({"app_name": app_name})
            
            if existing:
                # Update existing tool
                tool_doc["created_at"] = existing.get("created_at", datetime.utcnow())
                await tools_collection.update_one(
                    {"app_name": app_name},
                    {"$set": tool_doc}
                )
                logger.info(f"✓ Updated: {app_name} ({auth_config_id})")
                updated_count += 1
            else:
                # Insert new tool
                tool_doc["created_at"] = datetime.utcnow()
                await tools_collection.insert_one(tool_doc)
                logger.info(f"✓ Added: {app_name} ({auth_config_id})")
            
            synced_count += 1
        
        # Disable tools not in config
        all_tools_in_db = await tools_collection.find({}).to_list(None)
        disabled_count = 0
        
        for tool_doc in all_tools_in_db:
            app_name = tool_doc.get("app_name")
            if app_name not in enabled_tools:
                await tools_collection.update_one(
                    {"app_name": app_name},
                    {"$set": {
                        "enabled": False,
                        "updated_at": datetime.utcnow()
                    }}
                )
                logger.info(f"✗ Disabled: {app_name}")
                disabled_count += 1
        
        # Create indexes for better performance
        await tools_collection.create_index("app_name", unique=True)
        await tools_collection.create_index("category")
        await tools_collection.create_index("enabled")
        logger.info("Created indexes on tools collection")
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("SYNC COMPLETE!")
        logger.info("="*60)
        logger.info(f"New tools added: {synced_count - updated_count}")
        logger.info(f"Tools updated: {updated_count}")
        logger.info(f"Tools disabled: {disabled_count}")
        logger.info(f"Total enabled tools: {synced_count}")
        logger.info("="*60)
        
        # Close connection
        client.close()
        logger.info("MongoDB connection closed")
        
    except Exception as e:
        logger.error(f"Error syncing tools: {e}")
        raise


async def list_tools_in_db():
    """List all tools currently in the database."""
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        tools_collection = db["tools"]
        
        await client.admin.command('ping')
        logger.info("Connected to MongoDB")
        
        tools = await tools_collection.find({}).to_list(None)
        
        logger.info("\n" + "="*60)
        logger.info("TOOLS IN DATABASE")
        logger.info("="*60)
        
        enabled_tools = [t for t in tools if t.get("enabled", True)]
        disabled_tools = [t for t in tools if not t.get("enabled", True)]
        
        logger.info(f"\nEnabled Tools ({len(enabled_tools)}):")
        for tool in enabled_tools:
            logger.info(f"  ✓ {tool['app_name']}: {tool.get('auth_config_id', 'N/A')}")
            logger.info(f"    Category: {tool.get('category', 'N/A')}")
            logger.info(f"    Description: {tool.get('description', 'N/A')}")
        
        if disabled_tools:
            logger.info(f"\nDisabled Tools ({len(disabled_tools)}):")
            for tool in disabled_tools:
                logger.info(f"  ✗ {tool['app_name']}")
        
        logger.info("="*60)
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        # List tools in database
        asyncio.run(list_tools_in_db())
    else:
        # Sync tools to database
        asyncio.run(sync_tools_to_mongodb())


if __name__ == "__main__":
    main()
