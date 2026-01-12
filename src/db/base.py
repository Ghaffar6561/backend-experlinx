from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


Base = declarative_base()


class TimestampMixin:
    """
    Mixin class to add created_at and updated_at timestamp columns to models.
    """
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )


class UUIDPrimaryKeyMixin:
    """
    Mixin class to add a UUID primary key column to models.
    """
    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            unique=True,
            nullable=False
        )