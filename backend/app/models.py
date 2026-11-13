
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func,
)

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    full_name = Column(
        String(150),
        nullable=True,
    )

    role = Column(
        String(20),
        default="customer",
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    host = Column(
        String(255),
        nullable=False,
    )

    # SSH port
    port = Column(
        Integer,
        default=22,
        nullable=False,
    )

    # Node Agent port
    agent_port = Column(
        Integer,
        default=9000,
        nullable=False,
    )

    # Encrypted Agent token; never return this in API responses
    agent_token_encrypted = Column(
        Text,
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    city = Column(
        String(100),
        nullable=True,
    )

    description = Column(
        String(500),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    status = Column(
        String(20),
        default="unknown",
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
