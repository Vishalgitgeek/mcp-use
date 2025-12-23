"""Database connection models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    ORACLE = "oracle"
    BIGQUERY = "bigquery"


class DatabaseStatus(str, Enum):
    """Status of a database connection."""
    ACTIVE = "active"
    ERROR = "error"
    DISCONNECTED = "disconnected"


# ============================================================================
# Credential Schemas - Define what fields each database type needs
# ============================================================================

class PostgreSQLCredentials(BaseModel):
    """PostgreSQL connection credentials."""
    host: str = Field(..., description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    ssl: bool = Field(default=False, description="Use SSL connection")


class MySQLCredentials(BaseModel):
    """MySQL connection credentials."""
    host: str = Field(..., description="Database host")
    port: int = Field(default=3306, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    ssl: bool = Field(default=False, description="Use SSL connection")


class MongoDBCredentials(BaseModel):
    """MongoDB connection credentials."""
    connection_string: str = Field(..., description="MongoDB connection string (mongodb://...)")
    database: str = Field(..., description="Database name")


class OracleCredentials(BaseModel):
    """Oracle database connection credentials."""
    host: str = Field(..., description="Database host")
    port: int = Field(default=1521, description="Database port")
    service_name: str = Field(..., description="Oracle service name or SID")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")


class BigQueryCredentials(BaseModel):
    """Google BigQuery connection credentials."""
    project_id: str = Field(..., description="GCP Project ID")
    dataset: str = Field(..., description="BigQuery dataset name")
    credentials_json: str = Field(..., description="Service account JSON credentials (as string)")


# ============================================================================
# Schema Models - Describe database structure
# ============================================================================

class ColumnInfo(BaseModel):
    """Information about a database column."""
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False


class TableInfo(BaseModel):
    """Information about a database table."""
    name: str
    columns: List[ColumnInfo]


class DatabaseSchema(BaseModel):
    """Database schema information."""
    tables: List[TableInfo] = Field(default_factory=list)
    collections: List[str] = Field(default_factory=list)  # For MongoDB


# ============================================================================
# API Request/Response Models
# ============================================================================

class DatabaseConnectRequest(BaseModel):
    """Request to connect a database."""
    user_id: str = Field(..., description="User ID from your system")
    db_type: DatabaseType = Field(..., description="Type of database")
    credentials: Dict[str, Any] = Field(..., description="Database credentials")


class DatabaseTestRequest(BaseModel):
    """Request to test database connection without saving."""
    db_type: DatabaseType = Field(..., description="Type of database")
    credentials: Dict[str, Any] = Field(..., description="Database credentials")


class DatabaseDisconnectRequest(BaseModel):
    """Request to disconnect a database."""
    user_id: str = Field(..., description="User ID from your system")
    db_type: DatabaseType = Field(..., description="Type of database to disconnect")


class DatabaseConnectResponse(BaseModel):
    """Response after connecting a database."""
    success: bool
    message: str
    db_type: Optional[str] = None
    schema: Optional[DatabaseSchema] = None


class DatabaseTestResponse(BaseModel):
    """Response after testing a database connection."""
    success: bool
    message: str
    schema: Optional[DatabaseSchema] = None


class DatabaseInfo(BaseModel):
    """Information about a connected database."""
    db_type: str
    status: str
    schema: Optional[DatabaseSchema] = None
    connected_at: Optional[datetime] = None


class DatabaseListResponse(BaseModel):
    """Response listing user's connected databases."""
    databases: List[DatabaseInfo]


class DatabaseSchemaField(BaseModel):
    """Field definition for dynamic form rendering."""
    name: str
    type: str  # "string", "integer", "boolean", "password"
    required: bool
    default: Optional[Any] = None
    description: str


class DatabaseTypeInfo(BaseModel):
    """Information about a database type for UI rendering."""
    type: DatabaseType
    display_name: str
    description: str
    fields: List[DatabaseSchemaField]


# ============================================================================
# MongoDB Document Model
# ============================================================================

class UserDatabase(BaseModel):
    """User database document model for MongoDB."""
    user_id: str = Field(..., description="User ID")
    db_type: DatabaseType = Field(..., description="Database type")
    credentials_encrypted: str = Field(..., description="Encrypted credentials")
    schema: DatabaseSchema = Field(default_factory=DatabaseSchema)
    status: DatabaseStatus = Field(default=DatabaseStatus.ACTIVE)
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
