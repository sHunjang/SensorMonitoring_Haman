"""
backend/app/core/logging.py
애플리케이션 전역 로깅 설정 모듈.

- logging 표준 모듈을 사용하여 로그 포맷과 레벨을 설정한다.
"""

import logging
import sys
from typing import TextIO


def configure_logging(level_name: str) -> None:
    """
    로깅 설정을 초기화하는 함수.

    :param level_name: 문자열 형태의 로깅 레벨 (예: "DEBUG", "INFO")
    """
    # 문자열 로깅 레벨을 실제 상수로 변환한다.
    level = logging.INFO
    if level_name == "DEBUG":
        level = logging.DEBUG
    elif level_name == "WARNING":
        level = logging.WARNING
    elif level_name == "ERROR":
        level = logging.ERROR
    elif level_name == "CRITICAL":
        level = logging.CRITICAL

    # 출력 스트림을 표준 출력으로 설정한다.
    stream: TextIO = sys.stdout

    # 기본 로깅 설정을 구성한다.
    logging.basicConfig(
        level=level,
        stream=stream,
        # 시간, 로거 이름, 레벨, 메시지를 포함하는 포맷
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # FastAPI, uvicorn 등이 사용하는 루트 로거의 레벨도 맞춰준다.
    logging.getLogger().setLevel(level)
