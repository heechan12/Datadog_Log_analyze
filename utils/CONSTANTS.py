import streamlit as st

# Page Title
PG_Name_LOG_ANALYSIS = '상세 로그 분석 페이지'
PG_Name_USER_VERSION = "User/버전 별 분석 페이지"
PG_Name_HOW_TO = "사용법"

# Table Name
TB_Name_BYE_REASON ='BYE Reason'
TB_Name_CALL_END_REASON = 'Call End Reason'
TB_Name_CALL_START_TIME = '통화 시작 시간'
TB_Name_CAPTURE_CALLBACK = 'CaptureCallback 수'
TB_Name_FIRST_RX = 'FirstRx 수'
TB_Name_CALL_DURATION = '통화 유지 시간 (초)'
TB_Name_RECENT_HEALTH_CHECK = '최근 HealthCheck 수'
TB_Name_SRTP_ERROR = 'SRTP Error 수'
TB_Name_STOP_HOLEPUNCHING_CODE = 'StopHolePunching Code'

# UI
CSV_FILE_UPLOAD = "CSV 파일 업로드"

# Dataframe Name
DF_Name_RESOURCE_URL = 'Resource Url'

#Title Name
TITLE_BYE_REASON_ANALYSIS = "통화 종료 (BYE) 분석"
TITLE_FILTERED_DATA = "필터링 된 데이터"
TITLE_DEFAULT_DATA = "선택한 열 데이터 (전체 로그)"
TITLE_RTPTIMEOUT_PER_USER_ID = "User ID 별 RTP Timeout 개수"
TITLE_RTPTIMEOUT_PER_APP_VERSION = "앱 버전 별 RTP Timeout 개수"

def custom_divider(border_Size, color) :
    divider = st.markdown(f"""
            <hr style="border: {border_Size}px solid {color}; border-radius: 5px;">
        """, unsafe_allow_html=True)

    return divider