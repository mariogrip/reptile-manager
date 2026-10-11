import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, get_db
from .database import Base
from . import models, schemas, auth
from .config import settings
from .routers import animals, feedings, sheddings, breeding, custom_fields, ha, export, weights, lengths

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reptile Manager",
    description="Self-hosted reptile husbandry tracker with Home Assistant integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(animals.router,       prefix="/api/animals",       tags=["Animals"])
app.include_router(feedings.router,      prefix="/api/feedings",      tags=["Feedings"])
app.include_router(sheddings.router,     prefix="/api/sheddings",     tags=["Sheddings"])
app.include_router(weights.router,       prefix="/api/weights",       tags=["Weights"])
app.include_router(lengths.router,       prefix="/api/lengths",       tags=["Lengths"])
app.include_router(breeding.router,      prefix="/api/breeding",      tags=["Breeding"])
app.include_router(custom_fields.router, prefix="/api/custom-fields", tags=["Custom Fields"])
app.include_router(ha.router,            prefix="/api/ha",            tags=["Home Assistant"])
app.include_router(export.router,        prefix="/api/export",        tags=["export"])

@app.on_event("startup")
async def startup_event():
    """Startup: Tabellen anlegen, Migrationen, Default-Admin erstellen."""
    # ── Lightweight column migrations for SQLite ──────────────────────────────
    from sqlalchemy import text, inspect as sa_inspect
    with engine.connect() as conn:
        try:
            cols = [c["name"] for c in sa_inspect(engine).get_columns("animals")]
            migrations = [
                ("feeding_reminder_enabled", "BOOLEAN DEFAULT 1"),
                ("feeding_reminder_days",    "INTEGER"),
                ("status",      "VARCHAR(20) DEFAULT 'active'"),
                ("tracking_id", "VARCHAR(50)"),
                ("temp_day_c",    "REAL"),
                ("temp_night_c",  "REAL"),
                ("humidity_min",  "INTEGER"),
                ("humidity_max",  "INTEGER"),
                ("terrarium_size","VARCHAR(100)"),
                ("substrate",     "VARCHAR(200)"),
                ("uv_required",   "BOOLEAN"),
                ("lighting_hours","INTEGER"),
            ]
            for col, typedef in migrations:
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE animals ADD COLUMN {col} {typedef}"))
            # Sync status from legacy is_active
            conn.execute(text(
                "UPDATE animals SET status = CASE WHEN is_active = 0 THEN 'inactive' ELSE 'active' END "
                "WHERE status IS NULL OR status = ''"
            ))
            conn.commit()
        except Exception:
            pass
        # ha_config migrations
        try:
            ha_cols = [c["name"] for c in sa_inspect(engine).get_columns("ha_config")]
            for col, typedef in [
                ("breeder_name",     "VARCHAR(200)"),
                ("breeder_street",   "VARCHAR(200)"),
                ("breeder_zip_city", "VARCHAR(100)"),
                ("breeder_phone",    "VARCHAR(50)"),
            ]:
                if col not in ha_cols:
                    conn.execute(text(f"ALTER TABLE ha_config ADD COLUMN {col} {typedef}"))
            conn.commit()
        except Exception:
            pass
        # Seed measurement history from the single current value on existing animals
        for table, col in [("weights", "weight_g"), ("lengths", "length_cm")]:
            try:
                conn.execute(text(
                    f"INSERT INTO {table} (animal_id, date, {col}) "
                    f"SELECT id, COALESCE(updated_at, created_at, CURRENT_TIMESTAMP), {col} FROM animals "
                    f"WHERE {col} IS NOT NULL AND id NOT IN (SELECT DISTINCT animal_id FROM {table})"
                ))
                conn.commit()
            except Exception:
                pass
    db = next(get_db())
    try:
        if db.query(models.User).count() == 0:
            admin = models.User(
                username=settings.first_admin_username,
                hashed_password=auth.get_password_hash(settings.first_admin_password),
                is_admin=True,
                is_active=True,
            )
            db.add(admin)
        if db.query(models.HAConfig).count() == 0:
            db.add(models.HAConfig())
        db.commit()
    finally:
        db.close()

# ── Auth routes ───────────────────────────────────────────────────────────────

@app.post("/api/auth/token", response_model=schemas.Token, tags=["Auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(
        {"sub": user.username},
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse, tags=["Auth"])
async def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/api/dashboard", response_model=schemas.DashboardStats, tags=["Dashboard"])
async def dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    total_animals = db.query(models.Animal).count()
    active_animals = db.query(models.Animal).filter(models.Animal.is_active.is_(True)).count()
    total_feedings = db.query(models.Feeding).count()
    total_sheddings = db.query(models.Shedding).count()
    feedings_this_month = db.query(models.Feeding).filter(models.Feeding.date >= month_start).count()
    sheddings_this_month = db.query(models.Shedding).filter(models.Shedding.date >= month_start).count()

    # Per-animal feeding check (respects reminder_enabled + per-animal threshold)
    ha_cfg = db.query(models.HAConfig).first()
    global_threshold = ha_cfg.feeding_reminder_days if ha_cfg else 7

    active_animals_list = (
        db.query(models.Animal).filter(models.Animal.is_active.is_(True)).all()
    )

    animals_needing: list[schemas.AnimalNeedingFeeding] = []
    for a in active_animals_list:
        # Skip if reminder disabled for this animal
        if a.feeding_reminder_enabled is False:
            continue
        threshold = a.feeding_reminder_days or global_threshold
        last_feed = (
            db.query(models.Feeding)
            .filter(models.Feeding.animal_id == a.id, models.Feeding.accepted.is_(True))
            .order_by(models.Feeding.date.desc())
            .first()
        )
        days = None
        if last_feed:
            d = last_feed.date
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            days = (now - d).days

        if days is None or days >= threshold:
            animals_needing.append(schemas.AnimalNeedingFeeding(
                id=a.id,
                name=a.name,
                species=a.species,
                morph=a.morph,
                sex=a.sex.value if a.sex else "unknown",
                photo_url=a.photo_url,
                days_since_feeding=days,
                threshold_days=threshold,
            ))

    raw_feedings = (
        db.query(models.Feeding).order_by(models.Feeding.date.desc()).limit(8).all()
    )
    raw_sheddings = (
        db.query(models.Shedding).order_by(models.Shedding.date.desc()).limit(8).all()
    )

    def enrich_feeding(f):
        animal = db.query(models.Animal).filter(models.Animal.id == f.animal_id).first()
        return schemas.FeedingResponse(
            **{k: v for k, v in f.__dict__.items() if not k.startswith("_")},
            animal_name=animal.name if animal else None,
        )

    def enrich_shedding(s):
        animal = db.query(models.Animal).filter(models.Animal.id == s.animal_id).first()
        return schemas.SheddingResponse(
            **{k: v for k, v in s.__dict__.items() if not k.startswith("_")},
            animal_name=animal.name if animal else None,
        )

    return schemas.DashboardStats(
        total_animals=total_animals,
        active_animals=active_animals,
        total_feedings=total_feedings,
        total_sheddings=total_sheddings,
        feedings_this_month=feedings_this_month,
        sheddings_this_month=sheddings_this_month,
        animals_not_fed_7days=len(animals_needing),
        recent_feedings=[enrich_feeding(f) for f in raw_feedings],
        recent_sheddings=[enrich_shedding(s) for s in raw_sheddings],
        animals_needing_feeding=animals_needing,
    )

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
