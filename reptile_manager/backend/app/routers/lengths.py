from .. import models, schemas
from .measurements import make_router

router = make_router(models.Length, schemas.LengthResponse, schemas.LengthCreate, schemas.LengthUpdate, "Length")
