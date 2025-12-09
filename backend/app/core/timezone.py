# backend/app/core/timezone.py
from datetime import datetime
import pytz  # pip install pytz

KST = pytz.timezone("Asia/Seoul")

def now_kst_naive() -> datetime:
    """
    KST 기준 현재 시각을 timezone 정보 제거한 naive datetime 으로 반환.
    DB 컬럼이 timezone 없는 DateTime일 때 사용.
    """
    aware = datetime.now(KST)
    return aware.replace(tzinfo=None)
