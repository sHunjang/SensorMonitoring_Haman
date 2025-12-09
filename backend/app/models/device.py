"""
backend/app/models/device.py
센서 장비 정보를 저장하는 Device 테이블 모델.

이 테이블에는 장비 종류, IP, 포트, Modbus Unit ID 등의
'정적인 메타 정보'를 저장한다.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Device(Base):
    """
    센서 장비 하나를 표현하는 ORM 모델 클래스.

    이 클래스는 SQLAlchemy 의 Base 를 상속하여
    devices 라는 이름의 테이블로 매핑된다.
    """
    __tablename__ = "devices"

    # 기본 키. 자동 증가하는 정수 ID.
    id = Column(Integer, primary_key=True, index=True)

    # 장비 이름. 예: "온실_1", "히트펌프_1"
    name = Column(String(100), nullable=False, unique=True, index=True)

    # 장비 종류. 예: "greenhouse", "heatpump", "powermeter", "flowmeter"
    device_type = Column(String(50), nullable=False, index=True)

    # 장비 IP 주소. 예: "192.168.0.10"
    ip_address = Column(String(100), nullable=False)

    # Modbus TCP 포트. 기본값 502 사용을 가정한다.
    modbus_port = Column(Integer, nullable=False, default=502)

    # Modbus Unit ID (Slave ID). 1~247 범위 정수 사용을 가정한다.
    modbus_unit_id = Column(Integer, nullable=False, default=1)

    # 설치 위치 등의 설명. 필수는 아니므로 nullable=True 로 둔다.
    location = Column(String(200), nullable=True)

    # SensorData, PowerData 와의 관계 설정.
    # back_populates 옵션을 통해 양방향 접근을 가능하게 한다.
    sensor_data = relationship(
        "SensorData",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    power_data = relationship(
        "PowerData",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        디버깅 시 객체를 사람이 읽기 쉬운 문자열로 표현하기 위한 메서드.
        """
        return f"<Device id={self.id} name={self.name} type={self.device_type}>"
