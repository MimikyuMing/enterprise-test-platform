from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Execution(Base):
    __tablename__ = "execution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending", nullable=False
    )
    total_cases: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    passed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    failed: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    case_results: Mapped[list["CaseResult"]] = relationship(
        back_populates="execution", cascade="all, delete-orphan"
    )


class CaseResult(Base):
    __tablename__ = "case_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        ForeignKey("execution.id"), nullable=False, index=True
    )
    nodeid: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    execution: Mapped["Execution"] = relationship(back_populates="case_results")