"""
backend/app/models/sensor_data.py
일반 센서 데이터를 저장하는 SensorData 테이블 모델.

온습도, 조도, 유량 등의 시계열 데이터를 저장하며,
TimescaleDB 의 hypertable 로 변환하여 사용한다.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Index,
    func
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.timezone import now_kst_naive


class SensorData(Base):
    """
    일반 센서 데이터를 표현하는 ORM 모델 클래스.

    PK를 (device_id, timestamp) 복합 키로 두어
    TimescaleDB hypertable 요구사항을 만족시킨다.
    """
    __tablename__ = "sensor_data"

    # 측정 시각. UTC 기준 시각을 저장하는 것을 권장한다.
    timestamp = Column(
        DateTime(timezone=False),
        nullable=False,
        primary_key=True,
        server_default=func.now(),
        default=now_kst_naive,
    )

    # 어느 장비에서 읽은 값인지 나타내는 외래 키.
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    # 온도 값 (필요에 따라 두 채널까지 저장)
    temperature_1 = Column(Float, nullable=True)
    temperature_2 = Column(Float, nullable=True)

    # 습도 값
    humidity_1 = Column(Float, nullable=True)
    humidity_2 = Column(Float, nullable=True)

    # 조도 (빛의 세기)
    illuminance_1 = Column(Float, nullable=True)
    illuminance_2 = Column(Float, nullable=True)

    # 물/기름 유량 및 누적 사용량
    water_flow_rate = Column(Float, nullable=True)
    water_total_volume = Column(Float, nullable=True)

    oil_flow_rate = Column(Float, nullable=True)
    oil_total_volume = Column(Float, nullable=True)

    # Device 모델과의 관계 (양방향).
    device = relationship("Device", back_populates="sensor_data")

    # 자주 사용하는 조회 패턴을 고려하여 인덱스를 추가한다.
    __table_args__ = (
        # 특정 장비의 특정 기간 데이터를 빠르게 조회하기 위한 복합 인덱스
        Index("idx_sensor_time", "timestamp"),
    )

    def __repr__(self) -> str:
        """
        디버깅 시 사용하기 좋은 문자열 표현.
        """
        return (
            f"<SensorData device_id={self.device_id} time={self.timestamp}"
        )
