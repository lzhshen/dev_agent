import datetime
from random import randint
from typing import Optional

from sqlalchemy import DateTime, Integer, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


MODEL_STATUS = (
    STATUS_ALIVE,
    STATUS_DELETE,
) = range(2)


class BaseModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    uuid: Mapped[int] = mapped_column(
        Integer, index=True, unique=True, nullable=False, default=lambda: randint(1, 4_294_967_295))
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=STATUS_ALIVE)


class BusinessCtxModel(BaseModel):
    __tablename__ = "business_ctx"
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")


class UserStoryModel(BaseModel):
    __tablename__ = "user_story"
    business_ctx_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")


class AcceptanceCriteriaModel(BaseModel):
    __tablename__ = "acceptance_criteria"
    user_story_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="title")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=False, default="")
