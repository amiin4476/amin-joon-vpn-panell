
import ipaddress
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .database import get_db
from .models import Node, User
from .permissions import require_admin
from .node_security import encrypt_node_token
from .node_client import (
    NodeConnectionError,
    check_node_health,
    get_node_metrics,
)


router = APIRouter(
    prefix="/nodes",
    tags=["Node Management"],
)


def normalize_node_host(value: str | None) -> str | None:
    if value is None:
        return None

    host = value.strip()

    if not host:
        raise ValueError("آدرس سرور نمی‌تواند خالی باشد")

    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]

    try:
        address = ipaddress.ip_address(host)
        return address.compressed

    except ValueError:
        pass

    if any(char in host for char in "/?#@:"):
        raise ValueError("آدرس سرور معتبر نیست")

    if any(char.isspace() for char in host):
        raise ValueError("آدرس سرور معتبر نیست")

    try:
        host = host.rstrip(".").encode("idna").decode("ascii").lower()
    except UnicodeError:
        raise ValueError("نام دامنه معتبر نیست") from None

    if not host or len(host) > 253:
        raise ValueError("نام دامنه معتبر نیست")

    labels = host.split(".")

    for label in labels:
        if (
            not label
            or len(label) > 63
            or not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
                label,
            )
        ):
            raise ValueError("نام دامنه معتبر نیست")

    return host


class NodeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=22, ge=1, le=65535)
    agent_port: int = Field(default=443, ge=1, le=65535)
    agent_token: str = Field(min_length=32, max_length=512)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        return normalize_node_host(value)


class NodeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    host: str | None = Field(default=None, min_length=1, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    agent_port: int | None = Field(default=None, ge=1, le=65535)
    agent_token: str | None = Field(default=None, min_length=32, max_length=512)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str | None) -> str | None:
        return normalize_node_host(value)


class NodeResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    agent_port: int
    country: str | None
    city: str | None
    description: str | None
    is_active: bool
    status: str

    model_config = {
        "from_attributes": True
    }


def get_node_or_404(db: Session, node_id: int):
    node = db.query(Node).filter(
        Node.id == node_id
    ).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سرور پیدا نشد",
        )

    return node


def validate_node_agent(node: Node):
    if not node.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این سرور غیرفعال است",
        )

    if not node.agent_token_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="توکن Agent برای این سرور ثبت نشده است",
        )


@router.get("/stats/summary")
def node_summary(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    total = db.query(Node).count()

    active = db.query(Node).filter(
        Node.is_active.is_(True)
    ).count()

    inactive = db.query(Node).filter(
        Node.is_active.is_(False)
    ).count()

    status_counts = (
        db.query(
            Node.status,
            func.count(Node.id),
        )
        .group_by(Node.status)
        .all()
    )

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "statuses": {
            status_name: count
            for status_name, count in status_counts
        },
    }


@router.get("/", response_model=list[NodeResponse])
def list_nodes(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    country: str | None = Query(default=None, max_length=100),
    is_active: bool | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(Node)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Node.name.ilike(pattern),
                Node.host.ilike(pattern),
                Node.city.ilike(pattern),
                Node.country.ilike(pattern),
            )
        )

    if country:
        query = query.filter(Node.country == country)

    if is_active is not None:
        query = query.filter(Node.is_active == is_active)

    return (
        query.order_by(Node.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post("/{node_id}/health")
async def check_node(
    node_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    node = get_node_or_404(db, node_id)
    validate_node_agent(node)

    try:
        result = await check_node_health(
            host=node.host,
            port=node.agent_port,
            encrypted_token=node.agent_token_encrypted,
        )

        node.status = "online"
        db.commit()

        return {
            "status": "online",
            "node_id": node.id,
            "agent": result,
        }

    except (NodeConnectionError, ValueError):
        node.status = "offline"
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ارتباط با Agent سرور برقرار نشد",
        )


@router.get("/{node_id}/metrics")
async def node_metrics(
    node_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    node = get_node_or_404(db, node_id)
    validate_node_agent(node)

    try:
        metrics = await get_node_metrics(
            host=node.host,
            port=node.agent_port,
            encrypted_token=node.agent_token_encrypted,
        )

        node.status = "online"
        db.commit()

        return {
            "node_id": node.id,
            "node_name": node.name,
            "status": "online",
            "metrics": metrics,
        }

    except (NodeConnectionError, ValueError):
        node.status = "offline"
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="دریافت اطلاعات منابع سرور ناموفق بود",
        )


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return get_node_or_404(db, node_id)


@router.post(
    "/",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_node(
    data: NodeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    existing = db.query(Node).filter(
        Node.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این نام سرور قبلاً ثبت شده است",
        )

    node_data = data.model_dump(exclude={"agent_token"})

    node = Node(
        **node_data,
        agent_token_encrypted=encrypt_node_token(data.agent_token),
    )

    db.add(node)
    db.commit()
    db.refresh(node)

    return node


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: int,
    data: NodeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    node = get_node_or_404(db, node_id)

    changes = data.model_dump(
        exclude_unset=True,
        exclude={"agent_token"},
    )

    if "name" in changes and changes["name"] is not None:
        duplicate = db.query(Node).filter(
            Node.name == changes["name"],
            Node.id != node_id,
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="این نام برای سرور دیگری ثبت شده است",
            )

    for field, value in changes.items():
        setattr(node, field, value)

    if data.agent_token is not None:
        node.agent_token_encrypted = encrypt_node_token(
            data.agent_token
        )

    db.commit()
    db.refresh(node)

    return node


@router.delete("/{node_id}")
def delete_node(
    node_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    node = get_node_or_404(db, node_id)

    db.delete(node)
    db.commit()

    return {
        "status": "success",
        "message": "سرور با موفقیت حذف شد",
    }
