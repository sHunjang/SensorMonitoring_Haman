"""
frontend/main.py
PyQt 애플리케이션 진입점.

- APIClient 를 생성하고 MainWindow 에 주입한다.
"""

import sys

from PyQt6.QtWidgets import QApplication

from api_client.client import APIClient
from ui.main_window import MainWindow


def main() -> None:
    """
    PyQt 애플리케이션을 시작하는 함수.
    """
    # 백엔드 API 의 베이스 URL. 나중에 설정 파일로 분리할 수 있다.
    base_url = "http://localhost:8000/api/v1"

    api_client = APIClient(base_url=base_url)

    app = QApplication(sys.argv)
    window = MainWindow(api_client=api_client)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
