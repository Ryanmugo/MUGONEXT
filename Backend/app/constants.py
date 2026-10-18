"""
=========================================================
MUGONEXT
Application Constants & Enums
=========================================================

Central location for enums and application-wide constants.

Author:
MUGONEXT
"""

from enum import Enum


# =========================================================
# Company
# =========================================================


class CompanyStatus(str, Enum):
    """
    Represents the lifecycle/status of a company.
    """

    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class SubscriptionPlan(str, Enum):
    """
    Represents the subscription plan assigned to a company.
    """

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


# =========================================================
# Users
# =========================================================


class UserRole(str, Enum):
    """
    Represents a user's role inside a company.
    """

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class AccountStatus(str, Enum):
    """
    Represents the lifecycle/status of a user account.
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    DELETED = "deleted"


# =========================================================
# Uploads / Files
# =========================================================


class FileType(str, Enum):
    """
    Supported dataset file types.
    """

    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    JSON = "json"
    PARQUET = "parquet"


class StorageProvider(str, Enum):
    """
    Storage location/provider for uploaded files.
    """

    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"


class UploadSource(str, Enum):
    """
    Source through which a dataset was uploaded.
    """

    WEB = "web"
    API = "api"
    IMPORT = "import"
    INTEGRATION = "integration"


class UploadStatus(str, Enum):
    """
    Processing status of an uploaded dataset.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================================
# Forecasting
# =========================================================


class ForecastModel(str, Enum):
    """
    Forecasting models supported by MUGONEXT.
    """

    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ARIMA = "arima"
    SARIMA = "sarima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    PROPHET = "prophet"
    LSTM = "lstm"
    TRANSFORMER = "transformer"
    AUTO = "auto"


# =========================================================
# Recommendations
# =========================================================


class RecommendationPriority(str, Enum):
    """
    Priority level assigned to an AI recommendation.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =========================================================
# Recommendation Status
# =========================================================


class RecommendationStatus(str, Enum):
    """
    Processing status of an AI recommendation.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================================
# AI Providers
# =========================================================


class AIProvider(str, Enum):
    """
    AI provider used for generating AI outputs.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


# =========================================================
# Chat / RAG
# =========================================================


class ChatRole(str, Enum):
    """
    Role of a message inside an AI conversation.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """
    Type of message stored in a conversation.
    """

    TEXT = "text"
    DATA = "data"
    FORECAST = "forecast"
    RECOMMENDATION = "recommendation"
    SYSTEM = "system"


# =========================================================
# Audit
# =========================================================


class AuditAction(str, Enum):
    """
    Actions recorded by the audit system.
    """

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    FORECAST = "forecast"
    RECOMMENDATION = "recommendation"


# =========================================================
# Application Constants
# =========================================================


DEFAULT_LANGUAGE = "en"

DEFAULT_TIMEZONE = "UTC"

DEFAULT_CURRENCY = "USD"

DEFAULT_CHECKSUM_ALGORITHM = "sha256"

DEFAULT_PAGE_SIZE = 20

MAX_PAGE_SIZE = 100