from enum import Enum
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..db.base import Base


class UsageResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    tokens_used = Column(Integer, nullable=False)  # Tokens consumed by this invocation
    request_id = Column(UUID(as_uuid=True), nullable=False)  # Correlation ID for tracing
    response_status = Column(String(20), nullable=False)  # success/error/timeout
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds

    # Relationships
    user = relationship("User", backref="usage_logs")
    tool = relationship("Tool", backref="usage_logs")

    def __repr__(self):
        return f"<UsageLog(id={self.id}, user_id={self.user_id}, tool_id={self.tool_id}, timestamp={self.timestamp})>"