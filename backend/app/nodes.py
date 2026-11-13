
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import get_db
from .models import Node, User
from .permissions import require_admin


router = APIRouter(
    prefix="/nodes",
    tags=["Node Management"],
)


class NodeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(default=22, ge=1, le=65535)
    agent_port: int = Field(default=9000, ge=1, le=65535)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class NodeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    host: str | None = Field(default=None, min_length=1, max_length=255)
    port: int | None = Field(default=None, ge=1, le=65535)
    agent_port: int | None = Field(default=None, ge=1, le=65535)
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
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(Node).order_by(Node.id.desc()).all()


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

    node = Node(**data.model_dump())

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

    changes = data.model_dump(exclude_unset=True)

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
