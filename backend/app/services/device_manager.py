"""
backend/app/services/device_manager.py
Device 관련 비즈니스 로직을 담당하는 서비스 모듈.

- 장비 생성, 조회, 수정, 삭제 기능을 제공한다.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceManager:
    """
    Device 엔터티에 대한 CRUD 작업을 수행하는 클래스.

    이 클래스는 순수한 비즈니스 로직만 담당하며,
    FastAPI 라우터에서는 이 클래스를 호출하여 동작을 수행한다.
    """

    def __init__(self, db: Session) -> None:
        """
        생성자에서 SQLAlchemy 세션을 전달받아 보관한다.
        """
        self.db = db

    def create_device(self, data: DeviceCreate) -> Device:
        """
        새로운 장비를 생성하여 데이터베이스에 저장한다.

        :param data: 장비 생성에 필요한 정보가 담긴 Pydantic 객체
        :return: 생성된 Device ORM 객체
        """
        # 같은 이름의 장비가 이미 존재하는지 확인한다.
        existing: Optional[Device] = (
            self.db.query(Device)
            .filter(Device.name == data.name)
            .first()
        )
        if existing is not None:
            # 단순화를 위해 예외 대신 ValueError 를 사용한다.
            raise ValueError(f"Device with name '{data.name}' already exists")

        # Device ORM 객체를 생성한다.
        device = Device(
            name=data.name,
            device_type=data.device_type,
            ip_address=data.ip_address,
            modbus_port=data.modbus_port,
            modbus_unit_id=data.modbus_unit_id,
            location=data.location,
        )

        # 세션에 추가하고 커밋한다.
        self.db.add(device)
        self.db.commit()
        # 커밋 후 refresh 를 호출하면 생성된 ID 값을 포함한 최신 상태를 가져온다.
        self.db.refresh(device)

        return device

    def get_device(self, device_id: int) -> Optional[Device]:
        """
        ID 로 장비 하나를 조회한다.

        :param device_id: 조회할 장비의 ID
        :return: Device 객체 또는 None
        """
        device: Optional[Device] = self.db.query(Device).get(device_id)
        return device

    def list_devices(self) -> List[Device]:
        """
        모든 장비를 조회하여 리스트로 반환한다.

        :return: Device 객체 리스트
        """
        devices: List[Device] = self.db.query(Device).order_by(Device.id).all()
        return devices

    def update_device(self, device_id: int, data: DeviceUpdate) -> Optional[Device]:
        """
        기존 장비 정보를 수정한다.

        :param device_id: 수정할 장비 ID
        :param data: 수정 데이터 (부분 수정 허용)
        :return: 수정된 Device 객체 또는 None
        """
        device: Optional[Device] = self.get_device(device_id)
        if device is None:
            return None

        # 전달된 필드만 선택적으로 업데이트한다.
        if data.name is not None:
            device.name = data.name
        if data.device_type is not None:
            device.device_type = data.device_type
        if data.ip_address is not None:
            device.ip_address = data.ip_address
        if data.modbus_port is not None:
            device.modbus_port = data.modbus_port
        if data.modbus_unit_id is not None:
            device.modbus_unit_id = data.modbus_unit_id
        if data.location is not None:
            device.location = data.location

        self.db.commit()
        self.db.refresh(device)
        return device

    def delete_device(self, device_id: int) -> bool:
        """
        장비를 삭제한다.

        :param device_id: 삭제할 장비 ID
        :return: 삭제 성공 여부
        """
        device: Optional[Device] = self.get_device(device_id)
        if device is None:
            return False

        self.db.delete(device)
        self.db.commit()
        return True
