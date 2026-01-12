from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    replaced_by = Column(UUID(as_uuid=True), ForeignKey("refresh_tokens.id"), nullable=True)

    # Relationship
    user = relationship("User", backref="refresh_tokens")
    replacement = relationship("RefreshToken", remote_side=[id], post_update=True)

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"