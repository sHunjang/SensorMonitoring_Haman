"""
backend/app/schemas/device.py
Device 모델에 대한 Pydantic 스키마 정의.

- 요청(request)와 응답(response)에 사용된다.
"""

from pydantic import BaseModel, Field
from typing import Optional


class DeviceBase(BaseModel):
    """
    Device 공통 필드를 정의하는 기본 스키마.

    이 스키마는 이름, 장비 종류, IP 주소 등
    클라이언트와 주고받을 기본 정보를 담는다.
    """
    name: str = Field(..., description="장비 이름 (예: 온실_1)")
    device_type: str = Field(..., description="장비 종류 (예: greenhouse, heatpump)")
    ip_address: str = Field(..., description="장비 IP 주소")
    modbus_port: int = Field(502, description="Modbus TCP 포트 (기본값 502)")
    modbus_unit_id: int = Field(1, description="Modbus Unit ID (Slave ID)")
    location: Optional[str] = Field(None, description="설치 위치 또는 설명")


class DeviceCreate(DeviceBase):
    """
    장비 생성 요청에 사용하는 스키마.

    DeviceBase 와 내용이 같지만, 의미적으로 생성용으로 구분한다.
    """
    pass


class DeviceUpdate(BaseModel):
    """
    장비 수정 요청에 사용하는 스키마.

    부분 업데이트를 허용하기 위해 모든 필드를 Optional 로 둔다.
    """
    name: Optional[str] = Field(None, description="장비 이름")
    device_type: Optional[str] = Field(None, description="장비 종류")
    ip_address: Optional[str] = Field(None, description="장비 IP 주소")
    modbus_port: Optional[int] = Field(None, description="Modbus TCP 포트")
    modbus_unit_id: Optional[int] = Field(None, description="Modbus Unit ID")
    location: Optional[str] = Field(None, description="설치 위치 또는 설명")


class DeviceInDB(DeviceBase):
    """
    데이터베이스에 저장된 Device 객체를 표현하는 스키마.

    id 필드를 포함한다.
    """
    id: int = Field(..., description="데이터베이스 ID")

    class Config:
        """
        ORM 객체에서 이 스키마로 변환할 수 있도록 허용하는 설정.
        """
        from_attributes = True  # SQLAlchemy 모델 → Pydantic 스키마 변환 허용


class DeviceListResponse(BaseModel):
    """
    여러 개의 장비를 한 번에 반환할 때 사용하는 스키마.

    총 개수와 리스트를 함께 제공한다.
    """
    total: int = Field(..., description="총 장비 개수")
    devices: list[DeviceInDB] = Field(..., description="장비 목록")
