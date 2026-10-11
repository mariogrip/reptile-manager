from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import date, datetime
from enum import Enum

class Sex(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"

class FieldType(str, Enum):
    text = "text"
    number = "number"
    date = "date"
    boolean = "boolean"

# ── Custom Fields ─────────────────────────────────────────────────────────────

class CustomFieldBase(BaseModel):
    field_name: str
    field_value: Optional[str] = None
    field_type: FieldType = FieldType.text

class CustomFieldCreate(CustomFieldBase):
    pass

class CustomFieldUpdate(BaseModel):
    field_name: Optional[str] = None
    field_value: Optional[str] = None
    field_type: Optional[FieldType] = None

class CustomFieldResponse(CustomFieldBase):
    id: int
    animal_id: int

    model_config = {"from_attributes": True}

# ── Animals ───────────────────────────────────────────────────────────────────

class AnimalSummary(BaseModel):
    id: int
    name: str
    species: str
    common_name: Optional[str] = None
    morph: Optional[str] = None
    sex: Sex
    photo_url: Optional[str] = None
    tracking_id: Optional[str] = None
    status: str = 'active'

    model_config = {"from_attributes": True}


class AnimalBase(BaseModel):
    name: str
    species: str
    common_name: Optional[str] = None
    morph: Optional[str] = None
    sex: Sex = Sex.unknown
    date_of_birth: Optional[date] = None
    date_acquired: Optional[date] = None
    origin: Optional[str] = None
    weight_g: Optional[float] = None
    length_cm: Optional[float] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    mother_id: Optional[int] = None
    father_id: Optional[int] = None
    status:       str            = 'active'  # active | inactive | sold
    tracking_id:  Optional[str]  = None
    is_active:    bool           = True      # computed: status == 'active'
    feeding_reminder_enabled: bool = True
    notes: Optional[str] = None
    feeding_reminder_days: Optional[int] = None

    # Haltungsbedingungen
    temp_day_c:     Optional[float] = None
    temp_night_c:   Optional[float] = None
    humidity_min:   Optional[int]   = None
    humidity_max:   Optional[int]   = None
    terrarium_size: Optional[str]   = None
    substrate:      Optional[str]   = None
    uv_required:    Optional[bool]  = None
    lighting_hours: Optional[int]   = None

class AnimalCreate(AnimalBase):
    pass


class AnimalBulkCreate(BaseModel):
    """Create multiple animals at once (e.g. from a clutch)."""
    quantity: int
    animal_data: "AnimalCreate"

class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    common_name: Optional[str] = None
    morph: Optional[str] = None
    sex: Optional[Sex] = None
    date_of_birth: Optional[date] = None
    date_acquired: Optional[date] = None
    origin: Optional[str] = None
    weight_g: Optional[float] = None
    length_cm: Optional[float] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    mother_id: Optional[int] = None
    father_id: Optional[int] = None
    status:       Optional[str]  = None
    tracking_id:  Optional[str]  = None
    is_active:    Optional[bool] = None
    feeding_reminder_enabled: Optional[bool] = None
    feeding_reminder_days: Optional[int] = None
    temp_day_c:     Optional[float] = None
    temp_night_c:   Optional[float] = None
    humidity_min:   Optional[int]   = None
    humidity_max:   Optional[int]   = None
    terrarium_size: Optional[str]   = None
    substrate:      Optional[str]   = None
    uv_required:    Optional[bool]  = None
    lighting_hours: Optional[int]   = None

class AnimalResponse(AnimalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    custom_fields: List[CustomFieldResponse] = []
    mother: Optional[AnimalSummary] = None
    father: Optional[AnimalSummary] = None

    model_config = {"from_attributes": True}

# ── Feedings ──────────────────────────────────────────────────────────────────

class FeedingBase(BaseModel):
    date: datetime
    food_type: str
    food_size: Optional[str] = None
    food_weight_g: Optional[float] = None
    food_count: int = 1
    live: bool = False
    accepted: bool = True
    notes: Optional[str] = None

class FeedingCreate(FeedingBase):
    animal_id: int

class FeedingUpdate(BaseModel):
    date: Optional[datetime] = None
    food_type: Optional[str] = None
    food_size: Optional[str] = None
    food_weight_g: Optional[float] = None
    food_count: Optional[int] = None
    live: Optional[bool] = None
    accepted: Optional[bool] = None
    notes: Optional[str] = None

class FeedingResponse(FeedingBase):
    id: int
    animal_id: int
    animal_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ── Sheddings ─────────────────────────────────────────────────────────────────

class SheddingBase(BaseModel):
    date: datetime
    complete: bool = True
    in_one_piece: bool = True
    pre_shed_days: Optional[int] = None
    notes: Optional[str] = None

class SheddingCreate(SheddingBase):
    animal_id: int

class SheddingUpdate(BaseModel):
    date: Optional[datetime] = None
    complete: Optional[bool] = None
    in_one_piece: Optional[bool] = None
    pre_shed_days: Optional[int] = None
    notes: Optional[str] = None

class SheddingResponse(SheddingBase):
    id: int
    animal_id: int
    animal_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ── Weights ───────────────────────────────────────────────────────────────────

class WeightBase(BaseModel):
    date: datetime
    weight_g: float
    notes: Optional[str] = None

class WeightCreate(WeightBase):
    animal_id: int

class WeightUpdate(BaseModel):
    date: Optional[datetime] = None
    weight_g: Optional[float] = None
    notes: Optional[str] = None

class WeightResponse(WeightBase):
    id: int
    animal_id: int
    animal_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ── Lengths ───────────────────────────────────────────────────────────────────

class LengthBase(BaseModel):
    date: datetime
    length_cm: float
    notes: Optional[str] = None

class LengthCreate(LengthBase):
    animal_id: int

class LengthUpdate(BaseModel):
    date: Optional[datetime] = None
    length_cm: Optional[float] = None
    notes: Optional[str] = None

class LengthResponse(LengthBase):
    id: int
    animal_id: int
    animal_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

# ── Breeding ──────────────────────────────────────────────────────────────────

class BreedingEventBase(BaseModel):
    female_id: int
    male_id: int
    date_paired: Optional[date] = None
    date_separated: Optional[date] = None
    copulation_observed: bool = False
    date_eggs_or_birth: Optional[date] = None
    clutch_size: Optional[int] = None
    fertile_count: Optional[int] = None
    success: Optional[bool] = None
    notes: Optional[str] = None

class BreedingEventCreate(BreedingEventBase):
    pass

class BreedingEventUpdate(BaseModel):
    date_paired: Optional[date] = None
    date_separated: Optional[date] = None
    copulation_observed: Optional[bool] = None
    date_eggs_or_birth: Optional[date] = None
    clutch_size: Optional[int] = None
    fertile_count: Optional[int] = None
    success: Optional[bool] = None
    notes: Optional[str] = None

class BreedingEventResponse(BreedingEventBase):
    id: int
    female: AnimalSummary
    male: AnimalSummary
    created_at: datetime

    model_config = {"from_attributes": True}

# ── HA Config ─────────────────────────────────────────────────────────────────

class HAConfigUpdate(BaseModel):
    ha_url: Optional[str] = None
    ha_token: Optional[str] = None
    webhook_id: Optional[str] = None
    enabled: Optional[bool] = None
    notify_feeding: Optional[bool] = None
    notify_shedding: Optional[bool] = None
    notify_breeding: Optional[bool] = None
    feeding_reminder_days: Optional[int] = None
    breeder_name:     Optional[str] = None
    breeder_street:   Optional[str] = None
    breeder_zip_city: Optional[str] = None
    breeder_phone:    Optional[str] = None

class HAConfigResponse(BaseModel):
    id: int
    ha_url: Optional[str] = None
    webhook_id: Optional[str] = None
    enabled: bool
    notify_feeding: bool
    notify_shedding: bool
    notify_breeding: bool
    feeding_reminder_days: int
    breeder_name:     Optional[str] = None
    breeder_street:   Optional[str] = None
    breeder_zip_city: Optional[str] = None
    breeder_phone:    Optional[str] = None

    model_config = {"from_attributes": True}

# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    is_admin: bool

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

# ── Dashboard ─────────────────────────────────────────────────────────────────

class AnimalNeedingFeeding(BaseModel):
    id: int
    name: str
    species: str
    morph: Optional[str] = None
    sex: Sex
    photo_url: Optional[str] = None
    days_since_feeding: Optional[int] = None
    threshold_days: int

class WeightPoint(BaseModel):
    date: datetime
    weight_g: float

class AnimalWeightTrend(BaseModel):
    id: int
    name: str
    species: str
    photo_url: Optional[str] = None
    points: List[WeightPoint]   # oldest first

class DashboardStats(BaseModel):
    total_animals: int
    active_animals: int
    total_feedings: int
    total_sheddings: int
    feedings_this_month: int
    sheddings_this_month: int
    animals_not_fed_7days: int
    recent_feedings: List[FeedingResponse]
    recent_sheddings: List[SheddingResponse]
    animals_needing_feeding: List[AnimalNeedingFeeding] = []
    weight_trends: List[AnimalWeightTrend] = []
