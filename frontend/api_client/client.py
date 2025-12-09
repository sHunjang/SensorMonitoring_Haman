"""
frontend/api_client/client.py
백엔드 FastAPI 서버와 통신하기 위한 간단한 HTTP 클라이언트.

- requests 라이브러리를 사용하여 REST API 를 호출한다.
- 현재는 Device 관련 API 만 구현한다.
"""

import requests
from typing import Any, Dict, List, Optional


class APIClient:
    """
    백엔드 API 호출을 담당하는 클래스.

    이 클래스는 HTTP 요청/응답 처리를 캡슐화하여
    PyQt 코드에서 직접 requests 를 다루지 않도록 한다.
    """

    def __init__(self, base_url: str) -> None:
        """
        생성자에서 API 베이스 URL 을 저장한다.

        :param base_url: 예) "http://localhost:8000/api/v1"
        """
        # URL 마지막에 슬래시가 있으면 제거하여 일관성을 유지한다.
        if base_url.endswith("/"):
            self.base_url = base_url[:-1]
        else:
            self.base_url = base_url

    def _build_url(self, path: str) -> str:
        """
        내부적으로 사용할 URL 조립 함수.

        :param path: "/devices" 와 같은 상대 경로
        :return: 전체 URL 문자열
        """
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def create_device(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 장비를 생성하는 API 호출.

        :param payload: 장비 정보 (name, device_type, ip_address 등)
        :return: 서버가 반환한 JSON 응답 (dict 형태)
        :raises: requests.HTTPError
        """
        url = self._build_url("/devices")
        response = requests.post(url, json=payload)
        # 상태 코드가 4xx 또는 5xx 인 경우 예외를 발생시킨다.
        if response.status_code >= 400:
            raise requests.HTTPError(
                f"Device create failed: {response.status_code} {response.text}"
            )
        data: Dict[str, Any] = response.json()
        return data

    def list_devices(self) -> List[Dict[str, Any]]:
        """
        모든 장비 목록을 조회하는 API 호출.

        :return: 장비 하나당 dict 를 원소로 가지는 리스트
        :raises: requests.HTTPError
        """
        url = self._build_url("/devices")
        response = requests.get(url)
        if response.status_code >= 400:
            raise requests.HTTPError(
                f"Device list failed: {response.status_code} {response.text}"
            )
        data: Dict[str, Any] = response.json()
        # 백엔드에서 {"total": n, "devices": [...]} 형태로 주기 때문에,
        # 여기서는 devices 리스트만 추출한다.
        devices: List[Dict[str, Any]] = data.get("devices", [])
        return devices

    def get_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """
        특정 ID 의 장비를 조회하는 API 호출.

        :param device_id: 조회할 장비의 ID
        :return: 장비 정보 dict 또는 None
        :raises: requests.HTTPError
        """
        url = self._build_url(f"/devices/{device_id}")
        response = requests.get(url)
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise requests.HTTPError(
                f"Get device failed: {response.status_code} {response.text}"
            )
        data: Dict[str, Any] = response.json()
        return data
