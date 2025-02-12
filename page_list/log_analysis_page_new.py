import streamlit as st
import pandas as pd
from datetime import timedelta

from utils.CONSTANTS import (
    TB_Name_BYE_REASON, TB_Name_CAPTURE_CALLBACK, TB_Name_FIRST_RX, TB_Name_CALL_DURATION, TB_Name_CALL_START_TIME,
    TB_Name_RECENT_HEALTH_CHECK, TB_Name_SRTP_ERROR, PG_Name_LOG_ANALYSIS, CSV_FILE_UPLOAD,
    TB_Name_STOP_HOLEPUNCHING_CODE, TITLE_BYE_REASON_ANALYSIS, TITLE_FILTERED_DATA, TITLE_DEFAULT_DATA, TB_Name_CALL_END_REASON
)
from utils.sequence_diagram import generate_plantuml_sequence, render_plantuml
from utils.log_analyzer import (
    get_call_duration, get_recent_healthcheck_counts, get_srtp_error_count,
    get_bye_reasons, get_stopholepunching_code, get_call_end_reasons
)

'''
TODO : 딥러닝 기반으로 로그 분석
CHECKLIST : 변수명, 함수명 정리
'''

def load_and_process(file):
    # CSV 파일 읽고 시간 변환 및 URL 처리
    df = pd.read_csv(file)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce').dt.tz_localize(
        'UTC').dt.tz_convert('Asia/Seoul')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce').dt.tz_localize(
        'UTC').dt.tz_convert('Asia/Seoul')
    df['Resource Url'] = df['Resource Url'].str.replace('https://aicall-lgu.com/', '', regex=False)
    return df


def filter_valid_call_ids(df):
    """ 유효하지 않은 Call ID (None, Known 등) 제거 """
    valid_df = df[~df['context.callID'].isin([None, 'None', 'Known', 'Unknown'])].dropna(subset=['context.callID'])
    return valid_df


def display_call_analysis_table(df):
    st.subheader(f":orange-background[*{TITLE_BYE_REASON_ANALYSIS}*]")

    df = filter_valid_call_ids(df)

    # call_id_info = get_call_id_info(df)
    call_start_time = df[df['context.method'] == 'INVITE'].groupby('context.callID')['timestamp'].first().dt.strftime('%m-%d %H:%M:%S')
    call_end_reasons = get_call_end_reasons(df) 
    call_duration = get_call_duration(df).fillna('분석 불가')
    # TODO : 함수로 빼내고, table 에서는 5 이상인 경우 강조하기 
    capture_callback_count = df[df['context.method'] == 'CaptureCallback'].groupby('context.callID').size() \
                                  .reindex(df['context.callID'].unique(), fill_value=0)

    first_rx_count = df[df['Resource Url'].str.contains('firstRx', na=False)].groupby('context.callID').size() \
                     .reindex(df['context.callID'].unique(), fill_value=0)

    healthcheck_series = get_recent_healthcheck_counts(df)  # 이미 1D로 반환됨
    stop_holepunching_code = get_stopholepunching_code(df)  # 이미 1D로 반환됨
    srtp_error_count = get_srtp_error_count(df).reindex(call_duration.index, fill_value=0)
    # bye_reasons = get_bye_reasons(df).reindex(call_duration.index, fill_value='없음')

    # DataFrame 생성 시 모든 데이터를 1D로 보장
    call_analysis_table = pd.DataFrame({
        # "TB_Name_CALL_ID_INFO": call_id_info,
        TB_Name_CALL_START_TIME: call_start_time,
        TB_Name_CALL_END_REASON: call_end_reasons,
        # TB_Name_BYE_REASON: bye_reasons,
        TB_Name_CAPTURE_CALLBACK: capture_callback_count,
        TB_Name_FIRST_RX: first_rx_count,
        TB_Name_CALL_DURATION: call_duration.astype(str),
        TB_Name_RECENT_HEALTH_CHECK: healthcheck_series.astype(str),
        TB_Name_SRTP_ERROR: srtp_error_count.astype(int),
        TB_Name_STOP_HOLEPUNCHING_CODE: stop_holepunching_code.astype(str)
    })

    st.write(call_analysis_table)

    # Call Flow 분석
    with st.expander("### Call Flow 분석 (시퀀스 다이어그램)", expanded=False):
        call_ids = df['context.callID'].dropna().unique()
        # TODO : display_call_analysis_table 에서 선택된 call_id 를 가져오도록 수정
        selected_call_id = st.radio("Call ID 선택", options=call_ids)
        st.write(f"선택된 Call ID: {selected_call_id}")

        # 시퀀스 다이어그램 생성 및 출력
        plantuml_code = generate_plantuml_sequence(df, selected_call_id)
        diagram_content = render_plantuml(plantuml_code)
        st.text_area("시퀀스 다이어그램", diagram_content, height=400)


def log_analysis_page():
    st.title(PG_Name_LOG_ANALYSIS)

    uploaded_file = st.file_uploader(CSV_FILE_UPLOAD, type=["csv"])
    if uploaded_file is not None:
        df = load_and_process(uploaded_file)

        '''
        사이드 바 영역
        '''
        # 사이드바에서 원하는 열 선택
        st.sidebar.header("열 선택")
        columns_to_show = st.sidebar.multiselect(
            "보고 싶은 열을 선택하세요",
            df.columns.tolist(),
            default=[col for col in df.columns if col not in [
                'has_replay', 'status', 'timestamp', 'View name', 'Resource Duration', 'Resource Size',
                'Resource Status'
            ]]
        )

        # 필터링 옵션
        st.sidebar.header("필터")
        filter_condition = st.sidebar.radio("필터 조건", ["AND", "OR"])
        filtered_df = df.copy()
        filters = []

        for col in columns_to_show:
            unique_values = df[col].dropna().unique()
            if len(unique_values) > 0 and df[col].dtype == 'object':
                selected_values = st.sidebar.multiselect(f"{col} 선택", unique_values)
                if selected_values:
                    if filter_condition == "AND":
                        filters.append(filtered_df[col].isin(selected_values))
                    else:
                        filters.append(filtered_df[col].isin(selected_values))

        if filters:
            condition = pd.concat(filters, axis=1).all(axis=1) if filter_condition == "AND" else pd.concat(filters,
                                                                                                           axis=1).any(
                axis=1)
            filtered_df = filtered_df[condition]

        '''
        통화 종료 분석 테이블 영역
        '''
        with st.container(border=True):
            display_call_analysis_table(df)

        '''
        필터링 된 데이터 영역
        '''
        with st.container(border=True):
            st.subheader(f":orange-background[*{TITLE_FILTERED_DATA}*]")

            # 시간 필터링 위젯 추가
            min_time = filtered_df['timestamp'].min().to_pydatetime()
            max_time = filtered_df['timestamp'].max().to_pydatetime()

            time_range = st.slider(
                '시간 범위 선택',
                min_value=min_time,
                max_value=max_time,
                value=(min_time, max_time),
                step=timedelta(minutes=1),
                format="YYYY-MM-DD HH:mm"
            )

            # 시간 필터링 적용
            time_filtered_df = filtered_df[
                (filtered_df['timestamp'] >= time_range[0]) & (filtered_df['timestamp'] <= time_range[1])
                ]

            st.write(time_filtered_df[columns_to_show])

        '''
        기본 데이터 영역
        '''
        with st.container(border=True):
            st.subheader(f":orange-background[*{TITLE_DEFAULT_DATA}*]")
            st.write(df[columns_to_show])


if __name__ == "__main__":
    log_analysis_page()
