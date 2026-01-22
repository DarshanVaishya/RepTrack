from logging.config import fileConfig
import logging
from sqlalchemy import engine_from_config, text
from sqlalchemy import pool
from alembic import context
from app.database import Base
from app.models import (
    User,
    Exercise,
    WorkoutSet,
    Workout,
    WorkoutExercise,
    SessionExercise,
    SessionSet,
    WorkoutSession,
)
from app.config import get_settings

# Set up logging
logger = logging.getLogger("alembic.env")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Get database URL from your settings
settings = get_settings()
url = settings.database_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        logger.info("Running migrations in offline mode")
        context.run_migrations()
        logger.info("Offline migrations completed")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enable better error handling for PostgreSQL
            compare_type=True,
            compare_server_default=True,
        )

        # Get current migration version before running
        try:
            current_rev = context.get_context().get_current_revision()
            logger.info(f"Current database revision: {current_rev}")
        except Exception as e:
            logger.warning(f"Could not get current revision: {e}")

        with context.begin_transaction():
            logger.info("Starting migration transaction...")

            try:
                context.run_migrations()

                # Log the new revision after successful migration
                try:
                    new_rev = context.get_context().get_current_revision()
                    logger.info(
                        f"Migration completed successfully! New revision: {new_rev}"
                    )
                except Exception:
                    logger.info("Migration completed successfully!")

            except Exception as e:
                logger.error(f"Migration failed with error: {e}")
                raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
