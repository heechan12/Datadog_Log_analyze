from datetime import datetime, timezone, timedelta

# 시간 정리하기
def split_and_convert_iso_datetime(iso_str):
    try:
        # UTC 기준으로 파싱
        dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)

        # 한국 시간(KST, UTC+9)으로 변환
        kst_dt = dt.astimezone(timezone(timedelta(hours=9)))

        # 날짜 및 시간 분리
        date_part = kst_dt.date().isoformat()
        time_part = kst_dt.time().isoformat()

        return date_part, time_part
    except ValueError as e:
        return f"Invalid format: {e}"