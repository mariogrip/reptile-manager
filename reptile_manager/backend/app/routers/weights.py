from .. import models, schemas
from .measurements import make_router

router = make_router(models.Weight, schemas.WeightResponse, schemas.WeightCreate, schemas.WeightUpdate, "Weight")
