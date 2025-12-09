from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.power_data import PowerData
from app.schemas.power_data import PowerDataInDB

router = APIRouter(
    prefix="/power",
    tags=["power"],
)


@router.get(
    "/latest",
    response_model=List[PowerDataInDB],
    summary="특정 전력량계 장비의 최근 전력 데이터 조회",
)
def get_latest_power_data(
    device_id: int = Query(..., description="장비 ID"),
    limit: int = Query(200, ge=1, le=1000, description="가져올 최대 레코드 수"),
    db: Session = Depends(get_db),
) -> List[PowerDataInDB]:
    query = (
        db.query(PowerData)
        .filter(PowerData.device_id == device_id)
        .order_by(PowerData.timestamp.desc())
        .limit(limit)
    )
    rows = query.all()
    if not rows:
        raise HTTPException(status_code=404, detail="No power data found")

    return [PowerDataInDB.model_validate(r) for r in rows]
