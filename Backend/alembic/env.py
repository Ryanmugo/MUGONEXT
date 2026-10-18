from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.config import settings
from app.models.base import BaseModel

# Import ALL models so SQLAlchemy metadata knows about them.
from app.models.company import Company
from app.models.user import User
from app.models.upload import Upload
from app.models.forecast import Forecast
from app.models.recommendation import Recommendation
from app.models.chat_session import ChatSession


# =========================================================
# Alembic Config
# =========================================================

config = context.config


# =========================================================
# Logging
# =========================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# =========================================================
# Metadata
# =========================================================

target_metadata = BaseModel.metadata


# =========================================================
# Offline Migration
# =========================================================

def run_migrations_offline() -> None:
    """
    Run migrations without connecting to the database.
    """

    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================================================
# Online Migration
# =========================================================

def run_migrations_online() -> None:
    """
    Run migrations using an active database connection.
    """

    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# =========================================================
# Execute
# =========================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()