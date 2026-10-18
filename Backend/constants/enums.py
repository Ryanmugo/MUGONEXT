"""
=========================================================
MUGONEXT
Application Enums
=========================================================

Centralized enums used throughout the MUGONEXT platform.

Author:
MUGONEXT
"""

from enum import Enum


# =========================================================
# User & Authentication
# =========================================================


class UserRole(str, Enum):
    """
    Defines the permissions level of a user.
    """

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class AccountStatus(str, Enum):
    """
    Defines the current state of a user account.
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class LoginProvider(str, Enum):
    """
    Defines how a user authenticates.
    """

    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"


# =========================================================
# Company
# =========================================================


class SubscriptionPlan(str, Enum):
    """
    Defines the company's subscription tier.
    """

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class CompanyStatus(str, Enum):
    """
    Defines the current state of a company account.
    """

    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


# =========================================================
# Files & Uploads
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
    Defines where an uploaded file is stored.
    """

    LOCAL = "local"
    AWS_S3 = "aws_s3"
    CLOUDINARY = "cloudinary"
    GCP = "gcp"


class UploadSource(str, Enum):
    """
    Defines how a dataset entered MUGONEXT.
    """

    WEB = "web"
    API = "api"
    IMPORT = "import"
    INTEGRATION = "integration"


class UploadStatus(str, Enum):
    """
    Defines the processing state of an upload.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =========================================================
# Forecasting
# =========================================================


class ForecastModel(str, Enum):
    """
    Forecasting algorithms supported by MUGONEXT.
    """

    NAIVE = "naive"
    MOVING_AVERAGE = "moving_average"
    LINEAR_REGRESSION = "linear_regression"
    ARIMA = "arima"
    SARIMA = "sarima"
    PROPHET = "prophet"
    LSTM = "lstm"
    TRANSFORMER = "transformer"
    ENSEMBLE = "ensemble"


class ForecastStatus(str, Enum):
    """
    Defines the state of a forecast job.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================================
# Recommendations
# =========================================================


class RecommendationPriority(str, Enum):
    """
    Defines recommendation importance.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(str, Enum):
    """
    Defines the lifecycle of a recommendation.
    """

    NEW = "new"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


# =========================================================
# AI
# =========================================================


class AIProvider(str, Enum):
    """
    AI providers that MUGONEXT can use.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


class AIProcessingStatus(str, Enum):
    """
    Defines the state of an AI processing task.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =========================================================
# API Keys
# =========================================================


class APIKeyStatus(str, Enum):
    """
    Defines the state of an API key.
    """

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


# =========================================================
# Audit Logs
# =========================================================


class AuditAction(str, Enum):
    """
    Defines actions recorded by the audit system.
    """

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFIED = "email_verified"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FORECAST_CREATED = "forecast_created"
    RECOMMENDATION_CREATED = "recommendation_created"


# =========================================================
# Chat / RAG
# =========================================================


class ChatRole(str, Enum):
    """
    Defines the role of a message in an AI conversation.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSessionStatus(str, Enum):
    """
    Defines the state of an AI chat session.
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"