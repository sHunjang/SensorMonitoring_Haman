from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PowerDataInDB(BaseModel):
    timestamp: datetime = Field(..., description="측정 시각")
    device_id: int = Field(..., description="장비 ID")

    active_power: Optional[float] = None
    active_energy: Optional[float] = None

    class Config:
        from_attributes = True
