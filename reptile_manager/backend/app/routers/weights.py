from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter()

def sync_current_weight(animal: models.Animal, db: Session) -> None:
    """Keep Animal.weight_g equal to the most recent logged weight."""
    latest = (
        db.query(models.Weight)
        .filter(models.Weight.animal_id == animal.id)
        .order_by(models.Weight.date.desc(), models.Weight.id.desc())
        .first()
    )
    if latest:
        animal.weight_g = latest.weight_g

def log_weight_if_changed(animal: models.Animal, db: Session) -> None:
    """Record a weight entry when weight_g is set directly on the animal (e.g. edit form)."""
    if animal.weight_g is None:
        return
    latest = (
        db.query(models.Weight)
        .filter(models.Weight.animal_id == animal.id)
        .order_by(models.Weight.date.desc(), models.Weight.id.desc())
        .first()
    )
    if latest and latest.weight_g == animal.weight_g:
        return
    db.add(models.Weight(
        animal_id=animal.id,
        date=datetime.now(timezone.utc),
        weight_g=animal.weight_g,
    ))

def _enrich(w: models.Weight, db: Session) -> schemas.WeightResponse:
    animal = db.query(models.Animal).filter(models.Animal.id == w.animal_id).first()
    return schemas.WeightResponse(
        **{k: v for k, v in w.__dict__.items() if not k.startswith("_")},
        animal_name=animal.name if animal else None,
    )

@router.get("", response_model=List[schemas.WeightResponse])
@router.get("/", response_model=List[schemas.WeightResponse], include_in_schema=False)
def list_weights(
    skip: int = 0,
    limit: int = 100,
    animal_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    q = db.query(models.Weight)
    if animal_id:
        q = q.filter(models.Weight.animal_id == animal_id)
    weights = q.order_by(models.Weight.date.desc()).offset(skip).limit(limit).all()
    return [_enrich(w, db) for w in weights]

@router.post("", response_model=schemas.WeightResponse, status_code=201)
@router.post("/", response_model=schemas.WeightResponse, status_code=201, include_in_schema=False)
def create_weight(
    data: schemas.WeightCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    animal = db.query(models.Animal).filter(models.Animal.id == data.animal_id).first()
    if not animal:
        raise HTTPException(404, "Animal not found")
    if data.weight_g <= 0:
        raise HTTPException(422, "Weight must be positive")

    weight = models.Weight(**data.model_dump())
    db.add(weight)
    db.flush()
    sync_current_weight(animal, db)
    db.commit()
    db.refresh(weight)
    return _enrich(weight, db)

@router.put("/{weight_id}", response_model=schemas.WeightResponse)
def update_weight(
    weight_id: int,
    data: schemas.WeightUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    weight = db.query(models.Weight).filter(models.Weight.id == weight_id).first()
    if not weight:
        raise HTTPException(404, "Weight not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(weight, field, value)
    db.flush()
    sync_current_weight(weight.animal, db)
    db.commit()
    db.refresh(weight)
    return _enrich(weight, db)

@router.delete("/{weight_id}", status_code=204)
def delete_weight(
    weight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    weight = db.query(models.Weight).filter(models.Weight.id == weight_id).first()
    if not weight:
        raise HTTPException(404, "Weight not found")
    animal = weight.animal
    db.delete(weight)
    db.flush()
    sync_current_weight(animal, db)
    db.commit()
