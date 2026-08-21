from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func,DateTime,text
import uuid6
from uuid6 import uuid7
from datetime import datetime
from database.conn import engine
import uuid
from pgvector.sqlalchemy import Vector
class Base(DeclarativeBase):
    pass

class DevAgentTable(Base):
    __tablename__ = "devagent_table"

    id: Mapped[uuid.UUID] = mapped_column(nullable=False, default=uuid7, primary_key=True)
    content: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    source: Mapped[str] = mapped_column(nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(384),nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
Base.metadata.create_all(bind=engine)