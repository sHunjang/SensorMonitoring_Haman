"""
backend/app/services/collector.py
등록된 장비를 주기적으로 순회하며 센서 데이터를 수집하는 서비스.

- Device 테이블을 통해 장비 목록 조회
- ModbusService: 장비별 센서 값 조회
- SensorData 또는 PowerData 테이블에 시계열 데이터 저장
"""

import threading
import time
from typing import List

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.device import Device
from app.models.sensor_data import SensorData
from app.models.power_data import PowerData
from app.services.modbus_service import ModbusService

import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """
    백그라운드 스레드에서 데이터 수집 루프를 실행하는 클래스.
    """

    def __init__(self) -> None:
        """
        생성자에서 ModbusService 를 준비하고, 종료 플래그를 초기화한다.
        """
        self._modbus = ModbusService()
        self._stop_flag = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """
        데이터 수집 루프를 별도의 스레드에서 시작한다.
        """
        if self._thread is not None and self._thread.is_alive():
            # 이미 실행 중이면 무시
            return

        self._stop_flag = False
        self._thread = threading.Thread(
            target=self._run_loop,
            name="DataCollectorThread",
            daemon=True,
        )
        self._thread.start()
        logger.info("DataCollector started")

    def stop(self) -> None:
        """
        수집 루프 종료 플래그를 설정한다.
        """
        self._stop_flag = True
        logger.info("DataCollector stop requested")

    def _run_loop(self) -> None:
        """
        내부 수집 루프.

        - 주기적으로 DB에서 장비 목록을 조회
        - 장비별로 ModbusService 를 통해 센서 값 읽기
        - SensorData 또는 PowerData 로 저장
        """
        interval = settings.COLLECTION_INTERVAL
        logger.info("DataCollector loop running (interval: %s seconds)", interval)

        while not self._stop_flag:
            start_time = time.time()
            try:
                self._collect_once()
            except Exception as exc:
                logger.error("Error during data collection: %s", exc)

            elapsed = time.time() - start_time
            # 남은 시간만큼 sleep
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        logger.info("DataCollector loop stopped")

    def _collect_once(self) -> None:
        """
        한 번의 수집 사이클을 수행하는 함수.

        - DB 세션을 열고 모든 장비를 조회
        - 각 장비에 대해 적절한 테이블에 레코드 추가
        """
        db: Session = SessionLocal()
        try:
            devices: List[Device] = db.query(Device).all()
            if not devices:
                logger.info("No devices registered, skip collection")
                return

            logger.info("Collecting data from %d devices", len(devices))

            for dev in devices:
                data = self._modbus.read_sensors(dev.device_type)
                if not data:
                    continue

                if dev.device_type == "powermeter":
                    # 전력량계는 PowerData 테이블에 저장
                    record = PowerData(
                        device_id=dev.id,
                        active_power=data.get("active_power"),
                        active_energy=data.get("active_energy"),
                    )
                    db.add(record)
                else:
                    # 나머지 장비는 SensorData 테이블에 저장
                    record = SensorData(
                        device_id=dev.id,
                        temperature_1=data.get("temperature_1"),
                        temperature_2=data.get("temperature_2"),
                        humidity_1=data.get("humidity_1"),
                        humidity_2=data.get("humidity_2"),
                        illuminance_1=data.get("illuminance_1"),
                        illuminance_2=data.get("illuminance_2"),
                        water_flow_rate=data.get("water_flow_rate"),
                        water_total_volume=data.get("water_total_volume"),
                        oil_flow_rate=data.get("oil_flow_rate"),
                        oil_total_volume=data.get("oil_total_volume"),
                    )
                    db.add(record)

            db.commit()
            logger.info("Data collection cycle committed")

        finally:
            db.close()
