"""Shared logic for time-series measurements (weight, length) per animal."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db

# model -> the Animal column holding the current value (same name on both)
MEASUREMENTS = {
    models.Weight: "weight_g",
    models.Length: "length_cm",
}

def _latest(model, animal_id: int, db: Session):
    return (
        db.query(model)
        .filter(model.animal_id == animal_id)
        .order_by(model.date.desc(), model.id.desc())
        .first()
    )

def sync_current(model, animal: models.Animal, db: Session) -> None:
    """Keep the animal's current value equal to the most recent logged entry."""
    field = MEASUREMENTS[model]
    latest = _latest(model, animal.id, db)
    if latest:
        setattr(animal, field, getattr(latest, field))

def log_if_changed(model, animal: models.Animal, db: Session) -> None:
    """Record an entry when the value is set directly on the animal (e.g. edit form)."""
    field = MEASUREMENTS[model]
    value = getattr(animal, field)
    if value is None:
        return
    latest = _latest(model, animal.id, db)
    if latest and getattr(latest, field) == value:
        return
    db.add(model(animal_id=animal.id, date=datetime.now(timezone.utc), **{field: value}))

def log_all_if_changed(animal: models.Animal, db: Session, fields_set=None) -> None:
    for model, field in MEASUREMENTS.items():
        if fields_set is None or field in fields_set:
            log_if_changed(model, animal, db)

def make_router(model, response_schema, create_schema, update_schema, label: str) -> APIRouter:
    router = APIRouter()
    field = MEASUREMENTS[model]

    def _enrich(m, db: Session):
        animal = db.query(models.Animal).filter(models.Animal.id == m.animal_id).first()
        return response_schema(
            **{k: v for k, v in m.__dict__.items() if not k.startswith("_")},
            animal_name=animal.name if animal else None,
        )

    def _get(entry_id: int, db: Session):
        m = db.query(model).filter(model.id == entry_id).first()
        if not m:
            raise HTTPException(404, f"{label} not found")
        return m

    @router.get("", response_model=List[response_schema])
    @router.get("/", response_model=List[response_schema], include_in_schema=False)
    def list_entries(
        skip: int = 0,
        limit: int = 100,
        animal_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user),
    ):
        q = db.query(model)
        if animal_id:
            q = q.filter(model.animal_id == animal_id)
        return [_enrich(m, db) for m in q.order_by(model.date.desc()).offset(skip).limit(limit).all()]

    @router.post("", response_model=response_schema, status_code=201)
    @router.post("/", response_model=response_schema, status_code=201, include_in_schema=False)
    def create_entry(
        data: create_schema,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user),
    ):
        animal = db.query(models.Animal).filter(models.Animal.id == data.animal_id).first()
        if not animal:
            raise HTTPException(404, "Animal not found")
        if getattr(data, field) <= 0:
            raise HTTPException(422, f"{label} must be positive")
        m = model(**data.model_dump())
        db.add(m)
        db.flush()
        sync_current(model, animal, db)
        db.commit()
        db.refresh(m)
        return _enrich(m, db)

    @router.put("/{entry_id}", response_model=response_schema)
    def update_entry(
        entry_id: int,
        data: update_schema,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user),
    ):
        m = _get(entry_id, db)
        updates = data.model_dump(exclude_unset=True)
        if updates.get(field) is not None and updates[field] <= 0:
            raise HTTPException(422, f"{label} must be positive")
        for k, v in updates.items():
            setattr(m, k, v)
        db.flush()
        sync_current(model, m.animal, db)
        db.commit()
        db.refresh(m)
        return _enrich(m, db)

    @router.delete("/{entry_id}", status_code=204)
    def delete_entry(
        entry_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user),
    ):
        m = _get(entry_id, db)
        animal = m.animal
        db.delete(m)
        db.flush()
        sync_current(model, animal, db)
        db.commit()

    return router
