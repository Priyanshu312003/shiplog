import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PushEvent(Base):
    __tablename__ = "push_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Dedup: GitHub's unique delivery ID (from X-GitHub-Delivery header)
    delivery_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Which repo and branch
    repo_full_name: Mapped[str] = mapped_column(String(255))
    ref: Mapped[str] = mapped_column(String(255))

    # The two SHAs we need to fetch the diff (Stage 3)
    before_sha: Mapped[str] = mapped_column(String(40))
    after_sha: Mapped[str] = mapped_column(String(40))

    # Who pushed
    pusher_username: Mapped[str] = mapped_column(String(100))

    # Full raw payload stored as JSON string — insurance
    raw_payload: Mapped[str] = mapped_column(Text)

    # Pipeline status
    status: Mapped[str] = mapped_column(
        String(20),
        default="received",
        server_default="received",
    )

    # Auto-set on insert, never changes
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )