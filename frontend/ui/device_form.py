"""
frontend/ui/device_form.py
장비 등록/편집을 위한 PyQt 위젯.

- 장비 종류 선택 (콤보박스)
- 이름, IP, 포트, Unit ID, 위치 입력
- "등록" 버튼 클릭 시 APIClient 를 통해 백엔드에 전송
"""

from typing import Callable, Optional, Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)

from api_client.client import APIClient


class DeviceForm(QWidget):
    """
    장비 등록 폼 위젯.

    이 위젯은 부모로부터 APIClient 인스턴스를 전달받아,
    사용자가 입력한 값으로 백엔드에 장비 생성 요청을 보낸다.
    """

    def __init__(
        self,
        api_client: APIClient,
        on_created: Optional[Callable[[Dict[str, Any]], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        생성자.

        :param api_client: 백엔드와 통신할 APIClient 객체
        :param on_created: 장비 생성 성공 시 호출할 콜백 함수
        :param parent: 부모 위젯
        """
        super().__init__(parent)
        self.api_client = api_client
        self.on_created = on_created

        self._build_ui()

    def _build_ui(self) -> None:
        """
        폼에 들어갈 모든 위젯을 생성하고 배치한다.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 장비 종류 선택
        type_layout = QHBoxLayout()
        type_label = QLabel("장비 종류:", self)
        self.combo_type = QComboBox(self)
        # 장비 종류를 미리 정의한다.
        self.combo_type.addItem("온습도/조도 센서", "greenhouse")
        self.combo_type.addItem("히트펌프", "heatpump")
        self.combo_type.addItem("전력량계", "powermeter")
        self.combo_type.addItem("유량계", "flowmeter")

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.combo_type)

        # 이름 입력
        name_layout = QHBoxLayout()
        name_label = QLabel("장비 이름:", self)
        self.edit_name = QLineEdit(self)
        self.edit_name.setPlaceholderText("예: 온실_1")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.edit_name)

        # IP 입력
        ip_layout = QHBoxLayout()
        ip_label = QLabel("IP 주소:", self)
        self.edit_ip = QLineEdit(self)
        self.edit_ip.setPlaceholderText("예: 192.168.0.10")
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.edit_ip)

        # 포트 입력
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:", self)
        self.edit_port = QLineEdit(self)
        self.edit_port.setText("502")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.edit_port)

        # Unit ID 입력
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Unit ID:", self)
        self.edit_unit = QLineEdit(self)
        self.edit_unit.setText("1")
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.edit_unit)

        # 위치 입력
        loc_layout = QHBoxLayout()
        loc_label = QLabel("위치:", self)
        self.edit_location = QLineEdit(self)
        self.edit_location.setPlaceholderText("예: 1동 온실")
        loc_layout.addWidget(loc_label)
        loc_layout.addWidget(self.edit_location)

        # 등록 버튼
        self.btn_submit = QPushButton("장비 등록", self)
        self.btn_submit.clicked.connect(self.on_submit_clicked)

        # 레이아웃에 추가
        main_layout.addLayout(type_layout)
        main_layout.addLayout(name_layout)
        main_layout.addLayout(ip_layout)
        main_layout.addLayout(port_layout)
        main_layout.addLayout(unit_layout)
        main_layout.addLayout(loc_layout)
        main_layout.addWidget(self.btn_submit, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(main_layout)

    def on_submit_clicked(self) -> None:
        """
        "장비 등록" 버튼 클릭 시 호출되는 슬롯 함수.

        입력값을 검증하고, APIClient 를 사용하여 백엔드에 장비 생성 요청을 보낸다.
        """
        # 입력값 읽기
        name = self.edit_name.text().strip()
        ip = self.edit_ip.text().strip()
        port_text = self.edit_port.text().strip()
        unit_text = self.edit_unit.text().strip()
        location = self.edit_location.text().strip()
        device_type = self.combo_type.currentData()

        # 간단한 입력 검증
        if not name:
            QMessageBox.warning(self, "입력 오류", "장비 이름을 입력하세요.")
            return
        if not ip:
            QMessageBox.warning(self, "입력 오류", "IP 주소를 입력하세요.")
            return
        if not port_text.isdigit():
            QMessageBox.warning(self, "입력 오류", "Port 는 숫자여야 합니다.")
            return
        if not unit_text.isdigit():
            QMessageBox.warning(self, "입력 오류", "Unit ID 는 숫자여야 합니다.")
            return

        port = int(port_text)
        unit_id = int(unit_text)
        if port <= 0 or port > 65535:
            QMessageBox.warning(self, "입력 오류", "Port 범위가 올바르지 않습니다.")
            return
        if unit_id <= 0 or unit_id > 247:
            QMessageBox.warning(self, "입력 오류", "Unit ID 는 1~247 사이여야 합니다.")
            return

        # 요청 페이로드 구성
        payload: Dict[str, Any] = {
            "name": name,
            "device_type": device_type,
            "ip_address": ip,
            "modbus_port": port,
            "modbus_unit_id": unit_id,
            "location": location if location else None,
        }

        # 백엔드에 요청을 보낸다.
        try:
            created = self.api_client.create_device(payload)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "등록 실패",
                f"장비 등록 중 오류 발생:\n{exc}",
            )
            return

        # 성공 메시지
        QMessageBox.information(
            self,
            "등록 성공",
            f"장비가 등록되었습니다.\nID: {created.get('id')}",
        )

        # 콜백이 지정된 경우 호출 (예: 리스트 새로고침)
        if self.on_created is not None:
            self.on_created(created)

        # 폼 초기화
        self.edit_name.clear()
        # IP는 계속 입력할 수 있도록 남겨둘 수도 있지만, 여기서는 초기화하지 않는다.
