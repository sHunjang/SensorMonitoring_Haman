"""
backend/app/main.py
FastAPI 애플리케이션 엔트리포인트.

- 로깅 설정
- DB 초기화
- 라우터 등록
"""

from fastapi import FastAPI
import logging

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import init_db
from app.api.v1 import devices as devices_router
from app.api.v1 import sensors as sensors_router

# 더미 데이터 수집기
from app.services.collector import DataCollector

collector = DataCollector()

# 로깅 설정을 우선 구성한다.
configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션 인스턴스를 생성한다.
app = FastAPI(
    title="함안 시설원예연구소 센서 데이터 모니러링 API",
    version="1.0.0",
)


# 애플리케이션 시작 시 실행될 이벤트 핸들러
@app.on_event("startup")
def on_startup() -> None:
    """
    애플리케이션 시작 시 호출되는 함수.

    이 함수에서 데이터베이스를 초기화한다.
    """
    logger.info("Application startup: initializing database")
    init_db()
    logger.info("Database initialized")
    collector.start() # 데이터 수집기
    
@app.on_event("shutdown")
def on_shutdown() -> None:
    collector.stop()


# 라우터 등록
app.include_router(devices_router.router, prefix="/api/v1")
app.include_router(sensors_router.router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
    """
    간단한 헬스 체크 엔드포인트.

    프론트엔드에서 백엔드가 살아있는지 확인할 때 사용한다.
    """
    return {"status": "ok"}
