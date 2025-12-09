"""
backend/app/schemas/sensor_data.py
SensorData 조회용 Pydantic 스키마.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SensorDataInDB(BaseModel):
    """
    DB 에 저장된 SensorData 레코드를 표현하는 스키마.
    """
    # id: int = Field(..., description="레코드 ID")
    timestamp: datetime = Field(..., description="측정 시각")
    device_id: int = Field(..., description="장비 ID")

    temperature_1: Optional[float] = None
    temperature_2: Optional[float] = None
    humidity_1: Optional[float] = None
    humidity_2: Optional[float] = None
    illuminance_1: Optional[float] = None
    illuminance_2: Optional[float] = None
    water_flow_rate: Optional[float] = None
    water_total_volume: Optional[float] = None
    oil_flow_rate: Optional[float] = None
    oil_total_volume: Optional[float] = None

    class Config:
        from_attributes = True
