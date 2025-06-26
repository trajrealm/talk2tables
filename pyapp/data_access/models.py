import uuid
from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey, Text, DateTime, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.data_access.database import Base  # adjust this import to your app's base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    databases = relationship("UserDatabase", back_populates="user")
    queries = relationship("QueryHistory", back_populates="user")


class UserDatabase(Base):
    __tablename__ = "user_databases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    db_type = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    db_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="databases")
    schemas = relationship("UserDbSchema", back_populates="database", cascade="all, delete-orphan")
    queries = relationship("QueryHistory", back_populates="database")


class UserDbSchema(Base):
    __tablename__ = "user_db_schema"

    id = Column(Integer, primary_key=True, index=True)
    user_database_id = Column(Integer, ForeignKey("user_databases.id"), nullable=False)
    schema_name = Column(String, nullable=False)
    schema_json_info = Column(JSON, nullable=True)

    database = relationship("UserDatabase", back_populates="schemas")


class QueryHistory(Base):
    __tablename__ = "query_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user_db_id = Column(UUID(as_uuid=True), ForeignKey("user_databases.id", ondelete="CASCADE"))
    question = Column(Text, nullable=False)
    generated_sql = Column(Text)
    result = Column(JSON)
    success = Column(Boolean, default=False)
    error = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="queries")
    database = relationship("UserDatabase", back_populates="queries")
    feedback = relationship("QueryFeedback", back_populates="query", uselist=False)


class QueryFeedback(Base):
    __tablename__ = "query_feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("query_history.id", ondelete="CASCADE"))
    rating = Column(Integer)
    comment = Column(Text)

    query = relationship("QueryHistory", back_populates="feedback")

