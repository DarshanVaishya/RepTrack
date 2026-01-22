"""Utility functions for Alembic migrations"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def create_enum_if_not_exists(conn, enum_name, values):
    """
    Create PostgreSQL ENUM type only if it doesn't exist.

    Args:
        conn: SQLAlchemy connection
        enum_name: Name of the ENUM type
        values: List of ENUM values

    Returns:
        bool: True if created, False if already exists
    """
    result = conn.execute(
        sa.text(f"SELECT 1 FROM pg_type WHERE typname = '{enum_name}'")
    ).fetchone()

    if not result:
        enum_type = postgresql.ENUM(*values, name=enum_name)
        enum_type.create(conn)
        return True
    return False


def drop_enum_if_exists(conn, enum_name):
    """
    Drop PostgreSQL ENUM type if it exists.

    Args:
        conn: SQLAlchemy connection
        enum_name: Name of the ENUM type to drop
    """
    conn.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
