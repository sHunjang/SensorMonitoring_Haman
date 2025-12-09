"""
backend/app/core/config.py
애플리케이션 전역 설정을 관리하는 모듈.

- 환경변수 또는 기본값을 통해 설정을 정의한다.
- DB 접속 정보, 서버 포트, 데이터 수집 주기 등을 포함한다.
"""

import os


class Settings:
    """
    애플리케이션 설정 값을 보관하는 클래스.

    이 클래스는 단순한 속성 집합으로 동작하며,
    외부 라이브러리 의존성을 줄이기 위해 pydantic-settings 는 사용하지 않는다.
    """

    def __init__(self) -> None:
        """
        생성자에서 모든 설정 값을 한 번만 읽어온다.

        os.getenv() 는 표준 라이브러리 함수이므로 사용을 허용한다.
        """
        # 데이터베이스 접속 URL
        # 예: postgresql+psycopg2://user:password@localhost:5432/dbname
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:1234@localhost:5432/monitoring_haman"
        )

        # FastAPI 서버 설정
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))

        # 데이터 수집 주기 (초 단위)
        self.COLLECTION_INTERVAL = int(os.getenv("COLLECTION_INTERVAL", "5"))

        # Modbus 더미 모드 (True 이면 실제 통신 대신 랜덤 데이터 사용)
        dummy_value = os.getenv("DUMMY_MODE", "true").lower()
        self.DUMMY_MODE = dummy_value == "true"

        # 로깅 레벨
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# 전역 Settings 인스턴스를 하나만 생성해서 사용한다.
settings = Settings()
