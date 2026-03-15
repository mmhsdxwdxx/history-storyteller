from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    original_text = Column(Text)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 旧数据兼容字段（新版用 generation_results）
    vernacular_text = Column(Text)
    humorous_text = Column(Text)
    legacy_provider = Column(String(50))  # 记录旧数据使用的 provider

    versions = relationship("ContentVersion", back_populates="content")
    generations = relationship("GenerationResult", back_populates="content", order_by="desc(GenerationResult.created_at)")

class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    version_number = Column(Integer)
    field_name = Column(String(50))
    field_value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("Content", back_populates="versions")

class GenerationResult(Base):
    __tablename__ = "generation_results"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    vernacular_text = Column(Text)
    humorous_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("Content", back_populates="generations")

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    api_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=False)
    model = Column(String(100), nullable=False)
    is_default = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
