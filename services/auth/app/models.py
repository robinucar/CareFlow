from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    verification_challenges: Mapped[list["EmailVerificationChallenge"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )

    verification_security_state: Mapped["EmailVerificationSecurityState | None"] = (
        relationship(
            back_populates="account", cascade="all, delete-orphan", uselist=False
        )
    )


class EmailVerificationChallenge(Base):
    __tablename__ = "email_verification_challenges"
    __table_args__ = (
        Index(
            "uq_email_verification_open_challenge_per_account",
            "account_id",
            unique=True,
            postgresql_where=text("used_at IS NULL AND revoked_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.id"), nullable=False
    )
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    account: Mapped[UserAccount] = relationship(
        back_populates="verification_challenges"
    )


class EmailVerificationSecurityState(Base):
    __tablename__ = "email_verification_security_states"

    account_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.id"),
        primary_key=True,
    )
    failed_attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    failed_attempt_window_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resend_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    resend_window_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    account: Mapped[UserAccount] = relationship(
        back_populates="verification_security_state"
    )
