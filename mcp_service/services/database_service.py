"""Database connection service for handling user database connections."""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from cryptography.fernet import Fernet

from ..config import ENCRYPTION_KEY, SUPPORTED_DATABASES
from ..db.mongodb import get_collection
from ..models.database import (
    DatabaseType,
    DatabaseStatus,
    DatabaseSchema,
    TableInfo,
    ColumnInfo,
    DatabaseTypeInfo,
    DatabaseSchemaField,
)

logger = logging.getLogger("mcp.database")


class DatabaseService:
    """Service for managing user database connections."""

    def __init__(self):
        """Initialize the database service."""
        if ENCRYPTION_KEY:
            self._fernet = Fernet(ENCRYPTION_KEY.encode())
        else:
            self._fernet = None
            logger.warning("ENCRYPTION_KEY not set - database credentials will not be encrypted!")

    def _encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Encrypt credentials for storage."""
        json_str = json.dumps(credentials)
        if self._fernet:
            return self._fernet.encrypt(json_str.encode()).decode()
        return json_str  # Fallback: no encryption (not recommended)

    def _decrypt_credentials(self, encrypted: str) -> Dict[str, Any]:
        """Decrypt stored credentials."""
        if self._fernet:
            decrypted = self._fernet.decrypt(encrypted.encode()).decode()
            return json.loads(decrypted)
        return json.loads(encrypted)  # Fallback: not encrypted

    def get_supported_databases(self) -> List[DatabaseTypeInfo]:
        """Get list of supported database types with their credential schemas."""
        return [
            DatabaseTypeInfo(
                type=DatabaseType.POSTGRESQL,
                display_name="PostgreSQL",
                description="Open-source relational database",
                fields=[
                    DatabaseSchemaField(name="host", type="string", required=True, description="Database host"),
                    DatabaseSchemaField(name="port", type="integer", required=False, default=5432, description="Database port"),
                    DatabaseSchemaField(name="database", type="string", required=True, description="Database name"),
                    DatabaseSchemaField(name="username", type="string", required=True, description="Username"),
                    DatabaseSchemaField(name="password", type="password", required=True, description="Password"),
                    DatabaseSchemaField(name="ssl", type="boolean", required=False, default=False, description="Use SSL"),
                ]
            ),
            DatabaseTypeInfo(
                type=DatabaseType.MYSQL,
                display_name="MySQL",
                description="Popular open-source relational database",
                fields=[
                    DatabaseSchemaField(name="host", type="string", required=True, description="Database host"),
                    DatabaseSchemaField(name="port", type="integer", required=False, default=3306, description="Database port"),
                    DatabaseSchemaField(name="database", type="string", required=True, description="Database name"),
                    DatabaseSchemaField(name="username", type="string", required=True, description="Username"),
                    DatabaseSchemaField(name="password", type="password", required=True, description="Password"),
                    DatabaseSchemaField(name="ssl", type="boolean", required=False, default=False, description="Use SSL"),
                ]
            ),
            DatabaseTypeInfo(
                type=DatabaseType.MONGODB,
                display_name="MongoDB",
                description="Document-oriented NoSQL database",
                fields=[
                    DatabaseSchemaField(name="connection_string", type="string", required=True, description="Connection string (mongodb://...)"),
                    DatabaseSchemaField(name="database", type="string", required=True, description="Database name"),
                ]
            ),
            DatabaseTypeInfo(
                type=DatabaseType.ORACLE,
                display_name="Oracle",
                description="Enterprise relational database",
                fields=[
                    DatabaseSchemaField(name="host", type="string", required=True, description="Database host"),
                    DatabaseSchemaField(name="port", type="integer", required=False, default=1521, description="Database port"),
                    DatabaseSchemaField(name="service_name", type="string", required=True, description="Service name or SID"),
                    DatabaseSchemaField(name="username", type="string", required=True, description="Username"),
                    DatabaseSchemaField(name="password", type="password", required=True, description="Password"),
                ]
            ),
            DatabaseTypeInfo(
                type=DatabaseType.BIGQUERY,
                display_name="Google BigQuery",
                description="Google Cloud data warehouse",
                fields=[
                    DatabaseSchemaField(name="project_id", type="string", required=True, description="GCP Project ID"),
                    DatabaseSchemaField(name="dataset", type="string", required=True, description="Dataset name"),
                    DatabaseSchemaField(name="credentials_json", type="string", required=True, description="Service account JSON"),
                ]
            ),
        ]

    async def test_connection(self, db_type: DatabaseType, credentials: Dict[str, Any]) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """
        Test database connection and fetch schema.

        Returns:
            Tuple of (success, message, schema)
        """
        try:
            if db_type == DatabaseType.POSTGRESQL:
                return await self._test_postgresql(credentials)
            elif db_type == DatabaseType.MYSQL:
                return await self._test_mysql(credentials)
            elif db_type == DatabaseType.MONGODB:
                return await self._test_mongodb(credentials)
            elif db_type == DatabaseType.ORACLE:
                return await self._test_oracle(credentials)
            elif db_type == DatabaseType.BIGQUERY:
                return await self._test_bigquery(credentials)
            else:
                return False, f"Unsupported database type: {db_type}", None
        except Exception as e:
            logger.error(f"[DB] Connection test failed for {db_type}: {e}")
            return False, str(e), None

    async def _test_postgresql(self, credentials: Dict[str, Any]) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """Test PostgreSQL connection and fetch schema."""
        import asyncpg

        try:
            conn = await asyncpg.connect(
                host=credentials["host"],
                port=credentials.get("port", 5432),
                database=credentials["database"],
                user=credentials["username"],
                password=credentials["password"],
                ssl=credentials.get("ssl", False)
            )

            # Fetch schema
            schema = await self._fetch_postgresql_schema(conn)
            await conn.close()

            return True, "Connection successful", schema
        except Exception as e:
            return False, f"PostgreSQL connection failed: {str(e)}", None

    async def _fetch_postgresql_schema(self, conn) -> DatabaseSchema:
        """Fetch PostgreSQL database schema."""
        query = """
            SELECT
                t.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary
            FROM information_schema.tables t
            JOIN information_schema.columns c
                ON t.table_name = c.table_name AND t.table_schema = c.table_schema
            LEFT JOIN (
                SELECT ku.table_name, ku.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
            WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name, c.ordinal_position
        """

        rows = await conn.fetch(query)
        tables_dict: Dict[str, TableInfo] = {}

        for row in rows:
            table_name = row["table_name"]
            if table_name not in tables_dict:
                tables_dict[table_name] = TableInfo(name=table_name, columns=[])

            tables_dict[table_name].columns.append(
                ColumnInfo(
                    name=row["column_name"],
                    type=row["data_type"],
                    nullable=row["is_nullable"] == "YES",
                    primary_key=row["is_primary"]
                )
            )

        return DatabaseSchema(tables=list(tables_dict.values()))

    async def _test_mysql(self, credentials: Dict[str, Any]) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """Test MySQL connection and fetch schema."""
        import aiomysql

        try:
            conn = await aiomysql.connect(
                host=credentials["host"],
                port=credentials.get("port", 3306),
                db=credentials["database"],
                user=credentials["username"],
                password=credentials["password"],
            )

            # Fetch schema
            schema = await self._fetch_mysql_schema(conn, credentials["database"])
            conn.close()

            return True, "Connection successful", schema
        except Exception as e:
            return False, f"MySQL connection failed: {str(e)}", None

    async def _fetch_mysql_schema(self, conn, database: str) -> DatabaseSchema:
        """Fetch MySQL database schema."""
        async with conn.cursor() as cursor:
            query = """
                SELECT
                    t.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.COLUMN_KEY
                FROM information_schema.TABLES t
                JOIN information_schema.COLUMNS c
                    ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
                WHERE t.TABLE_SCHEMA = %s AND t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
            """

            await cursor.execute(query, (database,))
            rows = await cursor.fetchall()

        tables_dict: Dict[str, TableInfo] = {}

        for row in rows:
            table_name = row[0]
            if table_name not in tables_dict:
                tables_dict[table_name] = TableInfo(name=table_name, columns=[])

            tables_dict[table_name].columns.append(
                ColumnInfo(
                    name=row[1],
                    type=row[2],
                    nullable=row[3] == "YES",
                    primary_key=row[4] == "PRI"
                )
            )

        return DatabaseSchema(tables=list(tables_dict.values()))

    async def _test_mongodb(self, credentials: Dict[str, Any]) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """Test MongoDB connection and fetch schema."""
        from motor.motor_asyncio import AsyncIOMotorClient

        try:
            client = AsyncIOMotorClient(credentials["connection_string"])
            db = client[credentials["database"]]

            # Test connection
            await client.admin.command("ping")

            # Get collection names
            collections = await db.list_collection_names()

            client.close()

            return True, "Connection successful", DatabaseSchema(collections=collections)
        except Exception as e:
            return False, f"MongoDB connection failed: {str(e)}", None

    async def _test_oracle(self, credentials: Dict[str, Any]) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """Test Oracle connection and fetch schema."""
        try:
            import oracledb

            dsn = f"{credentials['host']}:{credentials.get('port', 1521)}/{credentials['service_name']}"

            conn = await oracledb.connect_async(
                user=credentials["username"],
                password=credentials["password"],
                dsn=dsn
            )

            # Fetch schema
            schema = await self._fetch_oracle_schema(conn, credentials["username"])
            await conn.close()

            return True, "Connection successful", schema
        except ImportError:
            return False, "Oracle driver (oracledb) not installed", None
        except Exception as e:
            return False, f"Oracle connection failed: {str(e)}", None

    async def _fetch_oracle_schema(self, conn, username: str) -> DatabaseSchema:
        """Fetch Oracle database schema."""
        async with conn.cursor() as cursor:
            query = """
                SELECT
                    t.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.NULLABLE,
                    CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 'Y' ELSE 'N' END as IS_PRIMARY
                FROM USER_TABLES t
                JOIN USER_TAB_COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
                LEFT JOIN (
                    SELECT cols.TABLE_NAME, cols.COLUMN_NAME
                    FROM USER_CONSTRAINTS cons
                    JOIN USER_CONS_COLUMNS cols ON cons.CONSTRAINT_NAME = cols.CONSTRAINT_NAME
                    WHERE cons.CONSTRAINT_TYPE = 'P'
                ) pk ON c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
                ORDER BY t.TABLE_NAME, c.COLUMN_ID
            """

            await cursor.execute(query)
            rows = await cursor.fetchall()

        tables_dict: Dict[str, TableInfo] = {}

        for row in rows:
            table_name = row[0]
            if table_name not in tables_dict:
                tables_dict[table_name] = TableInfo(name=table_name, columns=[])

            tables_dict[table_name].columns.append(
                ColumnInfo(
                    name=row[1],
                    type=row[2],
                    nullable=row[3] == "Y",
                    primary_key=row[4] == "Y"
                )
            )

        return DatabaseSchema(tables=list(tables_dict.values()))

    async def _test_bigquery(self, credentials: Dict[str, Any]) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """Test BigQuery connection and fetch schema."""
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account

            # Parse credentials JSON
            creds_dict = json.loads(credentials["credentials_json"])
            google_creds = service_account.Credentials.from_service_account_info(creds_dict)

            client = bigquery.Client(
                project=credentials["project_id"],
                credentials=google_creds
            )

            # Get tables in dataset
            dataset_ref = client.dataset(credentials["dataset"])
            tables = list(client.list_tables(dataset_ref))

            tables_info = []
            for table in tables[:20]:  # Limit to first 20 tables
                table_ref = dataset_ref.table(table.table_id)
                table_obj = client.get_table(table_ref)

                columns = [
                    ColumnInfo(
                        name=field.name,
                        type=field.field_type,
                        nullable=field.mode != "REQUIRED",
                        primary_key=False  # BigQuery doesn't have primary keys
                    )
                    for field in table_obj.schema
                ]

                tables_info.append(TableInfo(name=table.table_id, columns=columns))

            client.close()

            return True, "Connection successful", DatabaseSchema(tables=tables_info)
        except ImportError:
            return False, "BigQuery client (google-cloud-bigquery) not installed", None
        except Exception as e:
            return False, f"BigQuery connection failed: {str(e)}", None

    async def connect_database(
        self,
        user_id: str,
        db_type: DatabaseType,
        credentials: Dict[str, Any]
    ) -> tuple[bool, str, Optional[DatabaseSchema]]:
        """
        Connect a database for a user (test, fetch schema, and save).

        Returns:
            Tuple of (success, message, schema)
        """
        # Test connection and get schema
        success, message, schema = await self.test_connection(db_type, credentials)

        if not success:
            return False, message, None

        # Encrypt and store credentials
        encrypted_creds = self._encrypt_credentials(credentials)

        collection = await get_collection("user_databases")

        # Upsert (replace existing connection of same type)
        await collection.update_one(
            {"user_id": user_id, "db_type": db_type.value},
            {
                "$set": {
                    "credentials_encrypted": encrypted_creds,
                    "schema": schema.model_dump() if schema else {},
                    "status": DatabaseStatus.ACTIVE.value,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "connected_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        logger.info(f"[DB] User {user_id} connected {db_type.value} database")

        return True, "Database connected successfully", schema

    async def disconnect_database(self, user_id: str, db_type: DatabaseType) -> bool:
        """Disconnect a database for a user."""
        collection = await get_collection("user_databases")

        result = await collection.delete_one({
            "user_id": user_id,
            "db_type": db_type.value
        })

        if result.deleted_count > 0:
            logger.info(f"[DB] User {user_id} disconnected {db_type.value} database")
            return True
        return False

    async def get_user_databases(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all databases connected by a user."""
        collection = await get_collection("user_databases")
        cursor = collection.find({"user_id": user_id})
        databases = await cursor.to_list(length=100)

        return [
            {
                "db_type": db["db_type"],
                "status": db.get("status", "active"),
                "schema": db.get("schema", {}),
                "connected_at": db.get("connected_at")
            }
            for db in databases
        ]

    async def get_user_database(self, user_id: str, db_type: DatabaseType) -> Optional[Dict[str, Any]]:
        """Get a specific database connection for a user."""
        collection = await get_collection("user_databases")
        return await collection.find_one({
            "user_id": user_id,
            "db_type": db_type.value
        })

    async def execute_query(
        self,
        user_id: str,
        db_type: DatabaseType,
        query: str
    ) -> Dict[str, Any]:
        """
        Execute a query on user's database.

        Returns:
            Dict with success, result, or error
        """
        # Get user's database connection
        user_db = await self.get_user_database(user_id, db_type)

        if not user_db:
            return {"success": False, "error": f"No {db_type.value} database connected"}

        if user_db.get("status") != DatabaseStatus.ACTIVE.value:
            return {"success": False, "error": f"{db_type.value} database is not active"}

        # Decrypt credentials
        credentials = self._decrypt_credentials(user_db["credentials_encrypted"])

        try:
            if db_type == DatabaseType.POSTGRESQL:
                result = await self._execute_postgresql(credentials, query)
            elif db_type == DatabaseType.MYSQL:
                result = await self._execute_mysql(credentials, query)
            elif db_type == DatabaseType.MONGODB:
                return {"success": False, "error": "Use DB_MONGODB_FIND or DB_MONGODB_AGGREGATE for MongoDB"}
            elif db_type == DatabaseType.ORACLE:
                result = await self._execute_oracle(credentials, query)
            elif db_type == DatabaseType.BIGQUERY:
                result = await self._execute_bigquery(credentials, query)
            else:
                return {"success": False, "error": f"Unsupported database type: {db_type}"}

            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"[DB] Query execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_postgresql(self, credentials: Dict[str, Any], query: str) -> List[Dict]:
        """Execute query on PostgreSQL."""
        import asyncpg

        conn = await asyncpg.connect(
            host=credentials["host"],
            port=credentials.get("port", 5432),
            database=credentials["database"],
            user=credentials["username"],
            password=credentials["password"],
            ssl=credentials.get("ssl", False)
        )

        try:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def _execute_mysql(self, credentials: Dict[str, Any], query: str) -> List[Dict]:
        """Execute query on MySQL."""
        import aiomysql

        conn = await aiomysql.connect(
            host=credentials["host"],
            port=credentials.get("port", 3306),
            db=credentials["database"],
            user=credentials["username"],
            password=credentials["password"],
        )

        try:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                rows = await cursor.fetchall()
                return list(rows)
        finally:
            conn.close()

    async def _execute_oracle(self, credentials: Dict[str, Any], query: str) -> List[Dict]:
        """Execute query on Oracle."""
        import oracledb

        dsn = f"{credentials['host']}:{credentials.get('port', 1521)}/{credentials['service_name']}"

        conn = await oracledb.connect_async(
            user=credentials["username"],
            password=credentials["password"],
            dsn=dsn
        )

        try:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = await cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        finally:
            await conn.close()

    async def _execute_bigquery(self, credentials: Dict[str, Any], query: str) -> List[Dict]:
        """Execute query on BigQuery."""
        from google.cloud import bigquery
        from google.oauth2 import service_account

        creds_dict = json.loads(credentials["credentials_json"])
        google_creds = service_account.Credentials.from_service_account_info(creds_dict)

        client = bigquery.Client(
            project=credentials["project_id"],
            credentials=google_creds
        )

        try:
            query_job = client.query(query)
            results = query_job.result()
            return [dict(row) for row in results]
        finally:
            client.close()

    async def execute_mongodb_operation(
        self,
        user_id: str,
        operation: str,  # "find" or "aggregate"
        collection_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute MongoDB operation."""
        from motor.motor_asyncio import AsyncIOMotorClient

        user_db = await self.get_user_database(user_id, DatabaseType.MONGODB)

        if not user_db:
            return {"success": False, "error": "No MongoDB database connected"}

        credentials = self._decrypt_credentials(user_db["credentials_encrypted"])

        try:
            client = AsyncIOMotorClient(credentials["connection_string"])
            db = client[credentials["database"]]
            collection = db[collection_name]

            if operation == "find":
                query = params.get("query", {})
                limit = params.get("limit", 100)
                cursor = collection.find(query).limit(limit)
                results = await cursor.to_list(length=limit)
                # Convert ObjectId to string
                for doc in results:
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])
            elif operation == "aggregate":
                pipeline = params.get("pipeline", [])
                cursor = collection.aggregate(pipeline)
                results = await cursor.to_list(length=100)
                for doc in results:
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}

            client.close()
            return {"success": True, "result": results}
        except Exception as e:
            logger.error(f"[DB] MongoDB operation failed: {e}")
            return {"success": False, "error": str(e)}

    def format_schema_for_description(self, schema: Dict[str, Any]) -> str:
        """Format database schema for tool description."""
        if not schema:
            return "Schema not available"

        parts = []

        # SQL databases
        tables = schema.get("tables", [])
        if tables:
            for table in tables[:10]:  # Limit to first 10 tables
                cols = ", ".join([c["name"] for c in table.get("columns", [])[:8]])
                if len(table.get("columns", [])) > 8:
                    cols += ", ..."
                parts.append(f"{table['name']} ({cols})")

            if len(tables) > 10:
                parts.append(f"... and {len(tables) - 10} more tables")

        # MongoDB
        collections = schema.get("collections", [])
        if collections:
            parts.append(f"Collections: {', '.join(collections[:10])}")
            if len(collections) > 10:
                parts.append(f"... and {len(collections) - 10} more")

        return "; ".join(parts) if parts else "Schema not available"


# Singleton instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get the singleton DatabaseService instance."""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
