"""
backend/app/services/modbus_service.py
Modbus 장비와 통신하는 서비스.

현재 단계에서는 실제 Modbus 대신 난수를 이용한 더미 데이터
"""

import random
from typing import Dict, Any

from app.core.config import settings


class ModbusService:
    """
    Modbus 통신을 추상화한 서비스 클래스.

    실제 장비와 통신하는 구현으로 교체할 수 있도록 인터페이스를 단순하게 유지한다.
    """

    def __init__(self) -> None:
        """
        생성자에서 더미 모드 여부를 설정한다.
        """
        self.dummy_mode = settings.DUMMY_MODE

    def read_sensors(self, device_type: str) -> Dict[str, Any]:
        """
        장비 종류에 따라 센서 값을 읽어오는 메서드.

        :param device_type: "greenhouse", "heatpump", "powermeter", "flowmeter" 등
        :return: 센서 값 딕셔너리
        """
        if self.dummy_mode:
            return self._read_dummy(device_type)
        # 실제 Modbus 구현이 들어갈 자리
        raise NotImplementedError("실제 Modbus 통신은 아직 구현되지 않았습니다.")

    def _read_dummy(self, device_type: str) -> Dict[str, Any]:
        """
        더미 모드에서 사용할 난수 기반 센서 값 생성.

        장비 종류에 따라 필요한 필드만 채운다.
        """
        data: Dict[str, Any] = {}

        if device_type == "greenhouse":
            # 온실 환경: 온도/습도/조도
            data["temperature_1"] = round(random.uniform(18.0, 30.0), 2)
            data["temperature_2"] = round(random.uniform(18.0, 30.0), 2)
            data["humidity_1"] = round(random.uniform(40.0, 80.0), 2)
            data["humidity_2"] = round(random.uniform(40.0, 80.0), 2)
            data["illuminance_1"] = round(random.uniform(1000, 50000), 2)
            data["illuminance_2"] = round(random.uniform(100, 10000), 2)

        elif device_type == "heatpump":
            # 히트펌프: 입력/출력 온도 정도만 예시
            data["temperature_1"] = round(random.uniform(30.0, 60.0), 2)
            data["temperature_2"] = round(random.uniform(5.0, 20.0), 2)

        elif device_type == "powermeter":
            # 전력량계: active_power, active_energy
            data["active_power"] = round(random.uniform(0.0, 50.0), 2)
            data["active_energy"] = round(random.uniform(0.0, 100000.0), 2)

        elif device_type == "flowmeter":
            # 유량계: 순간 유량과 누적량
            data["water_flow_rate"] = round(random.uniform(0.0, 50.0), 2)
            data["water_total_volume"] = round(random.uniform(0.0, 100000.0), 2)

        else:
            # 정의되지 않은 타입은 비어있는 딕셔너리 반환
            pass

        return data