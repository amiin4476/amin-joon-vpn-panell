
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import get_db
from .models import Node, User
from .permissions import require_admin
from .node_security import encrypt_node_token


router = APIRouter(
    prefix="/nodes",
    tags=["Node Management"],
)


class NodeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=22, ge=1, le=65535)
    agent_port: int = Field(default=9000, ge=1, le=65535)
    agent_token: str = Field(min_length=32, max_length=512)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)


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


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سرور پیدا نشد",
        )

    return node


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
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سرور پیدا نشد",
        )

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
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سرور پیدا نشد",
        )

    db.delete(node)
    db.commit()

    return {
        "status": "success",
        "message": "سرور با موفقیت حذف شد",
    }
