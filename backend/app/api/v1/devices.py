"""
backend/app/api/v1/devices.py
장비(Device) 관련 HTTP API 라우터.

- 장비 등록
- 장비 목록 조회
- 장비 단건 조회
- 장비 수정
- 장비 삭제
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceInDB,
    DeviceListResponse,
)
from app.services.device_manager import DeviceManager


router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.post(
    "",
    response_model=DeviceInDB,
    status_code=status.HTTP_201_CREATED,
    summary="새 장비 등록",
)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
) -> DeviceInDB:
    """
    새로운 장비를 등록하는 엔드포인트.

    프론트엔드(PyQt)에서 장비 종류, IP, 포트 등을 입력하여
    이 엔드포인트로 전송하면 DB 에 저장된다.
    """
    manager = DeviceManager(db=db)
    try:
        device = manager.create_device(payload)
    except ValueError as exc:
        # 이미 같은 이름의 장비가 존재하는 경우 400 에러로 응답한다.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return DeviceInDB.model_validate(device)


@router.get(
    "",
    response_model=DeviceListResponse,
    summary="장비 목록 조회",
)
def list_devices(
    db: Session = Depends(get_db),
) -> DeviceListResponse:
    """
    등록된 모든 장비를 조회하는 엔드포인트.
    """
    manager = DeviceManager(db=db)
    devices = manager.list_devices()
    total = len(devices)
    device_schemas: List[DeviceInDB] = [
        DeviceInDB.model_validate(dev) for dev in devices
    ]
    return DeviceListResponse(total=total, devices=device_schemas)


@router.get(
    "/{device_id}",
    response_model=DeviceInDB,
    summary="장비 단건 조회",
)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
) -> DeviceInDB:
    """
    ID 로 특정 장비 하나를 조회하는 엔드포인트.
    """
    manager = DeviceManager(db=db)
    device = manager.get_device(device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    return DeviceInDB.model_validate(device)


@router.put(
    "/{device_id}",
    response_model=DeviceInDB,
    summary="장비 수정",
)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
) -> DeviceInDB:
    """
    기존 장비 정보를 수정하는 엔드포인트.

    부분 업데이트를 허용한다.
    """
    manager = DeviceManager(db=db)
    device = manager.update_device(device_id, payload)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
    return DeviceInDB.model_validate(device)


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="장비 삭제",
)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    장비를 삭제하는 엔드포인트.

    삭제 성공 시 본문 없는 204 상태 코드를 반환한다.
    """
    manager = DeviceManager(db=db)
    ok = manager.delete_device(device_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )
