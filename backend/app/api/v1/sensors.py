"""
backend/app/api/v1/sensors.py
센서 데이터 조회용 API.
(수집이 실제로 되고 있는지에 대한 확인용 API)

- 특정 장비의 최근 N개 SensorData 조회 엔드포인트.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sensor_data import SensorData
from app.schemas.sensor_data import SensorDataInDB

router = APIRouter(
    prefix="/sensors",
    tags=["sensors"],
)


@router.get(
    "/latest",
    response_model=List[SensorDataInDB],
    summary="특정 장비의 최근 센서 데이터 조회",
)
def get_latest_sensor_data(
    device_id: int = Query(..., description="장비 ID"),
    limit: int = Query(50, ge=1, le=500, description="가져올 최대 레코드 수"),
    db: Session = Depends(get_db),
) -> List[SensorDataInDB]:
    """
    주어진 장비 ID 에 대한 최근 SensorData 레코드를 조회한다.
    """
    query = (
        db.query(SensorData)
        .filter(SensorData.device_id == device_id)
        .order_by(SensorData.timestamp.desc())
        .limit(limit)
    )
    rows = query.all()
    if not rows:
        # 데이터가 없어도 굳이 에러를 줄 필요는 없지만, 여기서는 예시로 404 사용
        raise HTTPException(status_code=404, detail="No sensor data found")

    return [SensorDataInDB.model_validate(r) for r in rows]
