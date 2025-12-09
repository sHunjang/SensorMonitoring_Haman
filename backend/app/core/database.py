"""
backend/app/core/database.py
데이터베이스 연결 및 세션 관리를 담당하는 모듈.

- SQLAlchemy 엔진과 세션 팩토리를 생성한다.
- TimescaleDB 확장을 활성화하고 hypertable 을 생성하는 함수도 포함한다.
"""

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.core.config import settings

import logging


# 이 모듈 전용 로거 생성
logger = logging.getLogger(__name__)


# SQLAlchemy Base 클래스.
# 이 클래스를 상속한 모델들이 실제 테이블로 매핑된다.
Base = declarative_base()


# 데이터베이스 엔진 생성.
# echo=True 로 설정하면 실행되는 SQL 문이 모두 출력되므로 디버깅에 도움이 된다.
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True  # SQLAlchemy 2.x 스타일 사용
)


# 세션 팩토리 생성.
# 실제 세션 인스턴스는 SessionLocal() 호출로 얻는다.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의 의존성 주입에서 사용할 데이터베이스 세션 생성 함수.

    이 함수는 제너레이터로 구현되어 있으며,
    호출 시 세션을 yield 하고 finally 블록에서 세션을 닫는다.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    데이터베이스 초기화 함수.

    - 모든 모델을 import 하여 메타데이터에 등록한다.
    - Base.metadata.create_all() 을 호출하여 테이블을 생성한다.
    - TimescaleDB 확장을 활성화하고 hypertable 을 생성한다.
    """
    logger.info("Initializing database...")

    # 모델들을 import 해야 Base.metadata 가 모든 테이블을 인지한다.
    from app.models.device import Device  # noqa: F401
    from app.models.sensor_data import SensorData  # noqa: F401
    from app.models.power_data import PowerData  # noqa: F401

    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created")

    # TimescaleDB 설정
    _setup_timescaledb()


def _setup_timescaledb() -> None:
    """
    TimescaleDB 확장을 활성화하고,
    sensor_data, power_data 테이블을 hypertable 로 변환한다.

    이 함수는 PostgreSQL + TimescaleDB 환경을 전제로 한다.
    """
    logger.info("Configuring TimescaleDB...")

    # psycopg2 를 직접 쓰지 않고, SQLAlchemy 의 text() 를 사용한다.
    with engine.begin() as conn:
        try:
            # TimescaleDB 확장 활성화
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            logger.info("TimescaleDB extension enabled")

            # sensor_data 테이블을 hypertable 로 변환
            conn.execute(
                text(
                    """
                    SELECT create_hypertable(
                        'sensor_data',
                        'timestamp',
                        if_not_exists => TRUE
                    );
                    """
                )
            )

            # power_data 테이블을 hypertable 로 변환
            conn.execute(
                text(
                    """
                    SELECT create_hypertable(
                        'power_data',
                        'timestamp',
                        if_not_exists => TRUE
                    );
                    """
                )
            )

            logger.info("Hypertables created (sensor_data, power_data)")

        except Exception as exc:
            # TimescaleDB 가 없거나 이미 설정된 경우 경고만 출력하고 넘어간다.
            logger.warning("TimescaleDB setup warning: %s", exc)
