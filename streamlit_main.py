import streamlit as st
import pandas as pd
from datetime import datetime
import pytz


def load_data(file):
    df = pd.read_csv(file)
    # UTC 시간을 KST(한국 시간)으로 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Resource Url'] = df['Resource Url'].str.replace('https://aicall-lgu.com/', '', regex=False)
    df['Resource Url'] = df['Resource Url'].str.strip()  # 공백 제거
    return df


def get_call_duration(df):
    df_sorted = df.dropna(subset=['context.callID', 'timestamp']).sort_values(by=['context.callID', 'timestamp'])

    start_calls = df_sorted[df_sorted['Resource Url'].str.contains('res/ENGINE_startCall', case=False, na=False)]
    stop_calls = df_sorted[df_sorted['Resource Url'].str.contains('res/ENGINE_stopCall', case=False, na=False)]

    start_times = start_calls.groupby('context.callID')['timestamp'].first()
    stop_times = stop_calls.groupby('context.callID')['timestamp'].last()

    call_duration = (stop_times - start_times).dt.total_seconds().fillna('측정 불가')

    return call_duration


def get_recent_healthcheck_counts(df):
    healthcheck_df = df[df['Resource Url'].str.contains('res/ENGINE_ReceiveHealthCheck', case=False, na=False)]
    recent_counts = healthcheck_df.sort_values(by='timestamp', ascending=False).head(5)['@context.totalCount'].tolist()
    return recent_counts if recent_counts else ['없음']


def main():
    st.set_page_config(layout="wide")
    st.title("CSV 파일 분석 도구")

    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        df = load_data(uploaded_file)

        # RTP Timeout 분석
        st.write("### RTP Timeout 분석")
        capture_callback_count = df[df['context.method'] == 'CaptureCallback'].groupby('context.callID').size()
        first_rx_count = df[df['Resource Url'].str.contains('firstRx', na=False)].groupby('context.callID').size()
        call_duration = get_call_duration(df)
        healthcheck_counts = get_recent_healthcheck_counts(df)

        rtp_analysis = pd.DataFrame({
            'CaptureCallback Count': capture_callback_count,
            'FirstRx Count': first_rx_count,
            'Call Duration (seconds)': call_duration,
            'Recent HealthCheck Counts': [healthcheck_counts]
        }).fillna('측정 불가')

        st.write(rtp_analysis)

        # 사이드바에서 원하는 열 선택
        st.sidebar.header("열 선택")
        columns_to_show = st.sidebar.multiselect("보고 싶은 열을 선택하세요", df.columns.tolist(), default=df.columns.tolist())

        st.write("### 선택한 열 데이터")
        st.write(df[columns_to_show])

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
            if filter_condition == "AND":
                filtered_df = filtered_df.loc[pd.concat(filters, axis=1).all(axis=1)]
            else:
                filtered_df = filtered_df.loc[pd.concat(filters, axis=1).any(axis=1)]

        st.write("### 필터링된 데이터")
        st.write(filtered_df[columns_to_show])


if __name__ == "__main__":
    main()
