"""
backend/app/models/power_data.py
전력량계 데이터를 저장하는 PowerData 테이블 모델.

전력량계는 일반 센서와 달리 전력/전력량 중심의 데이터를 갖기 때문에
별도의 테이블로 분리하여 관리한다.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.timezone import now_kst_naive


class PowerData(Base):
    """
    전력 데이터를 표현하는 ORM 모델 클래스.

    이 클래스는 power_data 테이블로 매핑되며,
    각 행은 특정 시각에 특정 전력량계에서 읽은 전력 값을 의미한다.
    """
    __tablename__ = "power_data"

    # 측정 시각. UTC 기준 시각 사용을 권장한다.
    timestamp = Column(
        DateTime(timezone=False),
        nullable=False,
        primary_key=True,
        server_default=func.now(),
        default=now_kst_naive,
    )

    # 어느 장비(전력량계)에서 읽은 값인지 나타내는 외래 키.
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    # 유효전력 (kW)
    active_power = Column(Float, nullable=True)

    # 유효전력량 (kWh)
    active_energy = Column(Float, nullable=True)

    # Device 모델과의 관계 (양방향).
    device = relationship("Device", back_populates="power_data")

    __table_args__ = (
        # 특정 전력량계의 특정 기간 데이터를 빠르게 조회하기 위한 복합 인덱스
        Index("idx_power_time", "timestamp"),
    )

    def __repr__(self) -> str:
        """
        디버깅 시 사용하기 좋은 문자열 표현.
        """
        return (
            f"<PowerData id={self.id} device_id={self.device_id} "
            f"time={self.timestamp}>"
        )
