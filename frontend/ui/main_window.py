"""
frontend/ui/main_window.py
PyQt 메인 윈도우.

- 장비 등록 폼(DeviceForm)을 중앙에 배치한다.
- 나중에 장비 목록, 그래프 뷰 등을 여기에 추가할 수 있다.
"""

from typing import Dict, Any, List

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
)

from api_client.client import APIClient
from ui.device_form import DeviceForm


class MainWindow(QMainWindow):
    """
    애플리케이션 메인 윈도우.

    왼쪽에 장비 목록, 오른쪽에 장비 등록 폼을 두는 간단한 레이아웃으로 시작한다.
    """

    def __init__(self, api_client: APIClient, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.api_client = api_client

        self.setWindowTitle("온실 모니터링 시스템 - 장비 관리")
        self.resize(900, 600)

        self._build_ui()
        self.refresh_device_list()

    def _build_ui(self) -> None:
        """
        메인 레이아웃과 하위 위젯들을 생성한다.
        """
        central = QWidget(self)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 장비 목록 라벨
        label_list = QLabel("등록된 장비 목록", self)

        # 장비 목록 위젯
        self.list_devices = QListWidget(self)

        # 장비 등록 폼
        self.device_form = DeviceForm(
            api_client=self.api_client,
            on_created=self.on_device_created,
            parent=self,
        )

        main_layout.addWidget(label_list)
        main_layout.addWidget(self.list_devices, stretch=2)
        main_layout.addWidget(self.device_form, stretch=1)

        self.setCentralWidget(central)

    def refresh_device_list(self) -> None:
        """
        백엔드에서 장비 목록을 조회하여 리스트 위젯을 갱신한다.
        """
        self.list_devices.clear()
        try:
            devices: List[Dict[str, Any]] = self.api_client.list_devices()
        except Exception as exc:
            # 간단히 리스트에 에러 메시지를 추가한다.
            item = QListWidgetItem(f"장비 목록 조회 실패: {exc}")
            self.list_devices.addItem(item)
            return

        for dev in devices:
            name = dev.get("name", "unknown")
            dtype = dev.get("device_type", "unknown")
            ip = dev.get("ip_address", "unknown")
            item_text = f"[{dev.get('id')}] {name} ({dtype}) {ip}"
            item = QListWidgetItem(item_text)
            self.list_devices.addItem(item)

    def on_device_created(self, device: Dict[str, Any]) -> None:
        """
        DeviceForm 에서 장비 생성 성공 시 호출되는 콜백.

        단순히 목록을 다시 불러온다.
        """
        self.refresh_device_list()

