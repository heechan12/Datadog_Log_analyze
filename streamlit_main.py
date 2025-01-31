import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import graphviz as graphviz


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
    call_duration = (stop_times - start_times).dt.total_seconds()
    return call_duration


def get_recent_healthcheck_counts(df):
    healthcheck_df = df[df['Resource Url'].str.contains('res/ENGINE_ReceiveHealthCheck', case=False, na=False)]
    recent_counts = healthcheck_df.sort_values(by='timestamp', ascending=False).head(5)['@context.totalCount'].tolist()
    return ', '.join(map(str, recent_counts)) if recent_counts else '없음'


def get_srtp_error_count(df):
    srtp_error_count = df[
        df['Resource Url'].str.contains('res/ENGINE_errorSrtpDepacketizer', case=False, na=False)].groupby(
        'context.callID').size()
    return srtp_error_count


def get_bye_reasons(df):
    bye_reasons = df[df['context.method'] == 'BYE'].groupby('context.callID')['context.reasonFromLog'].first().fillna(
        '없음')
    return bye_reasons


def generate_sequence_diagram(df, call_id):
    call_flow_df = df[(df['context.callID'] == call_id) & (
        df['Resource Url'].str.contains('res/SDK_restReq|res/SDK_longRes', case=False, na=False))].sort_values(
        by='timestamp')
    if call_flow_df.empty:
        return "선택된 Call ID에 유효한 메시지(REST 요청 또는 응답)가 없습니다."

    # Initialize Graphviz Digraph
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', size='10,5')

    # Define entities
    dot.node("UE", "UE", shape="box")
    dot.node("Server", "Server", shape="box")

    # Iterate through messages
    for _, row in call_flow_df.iterrows():
        timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['timestamp']) else 'Unknown Time'
        method = row['context.method']
        url = row['Resource Url']
        direction = "UE -> Server" if 'res/SDK_restReq' in url else "Server -> UE" if 'res/SDK_longRes' in url else None

        if direction == "UE -> Server":
            dot.edge("UE", "Server", label=f"{timestamp}\n{method}")
        elif direction == "Server -> UE":
            dot.edge("Server", "UE", label=f"{timestamp}\n{method}")

    return dot


def main():
    st.set_page_config(layout="wide")
    st.title("CSV 파일 분석 도구")

    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        df = df.dropna(subset=['context.callID'])  # NaN인 Call ID 제거

        # RTP Timeout 분석
        st.write("### RTP Timeout 분석")
        capture_callback_count = df[df['context.method'] == 'CaptureCallback'].groupby('context.callID').size().reindex(
            df['context.callID'].unique(), fill_value=0)
        first_rx_count = df[df['Resource Url'].str.contains('firstRx', na=False)].groupby(
            'context.callID').size().reindex(df['context.callID'].unique(), fill_value=0)
        call_duration = get_call_duration(df).fillna(0)
        healthcheck_counts = get_recent_healthcheck_counts(df)
        healthcheck_series = pd.Series(healthcheck_counts, index=call_duration.index).fillna('없음')
        srtp_error_count = get_srtp_error_count(df).reindex(call_duration.index, fill_value=0)  # SRTP Error 개수
        bye_reasons = get_bye_reasons(df).reindex(call_duration.index).fillna('없음')  # BYE 이유

        # 모든 열의 길이를 call_duration 기준으로 맞춤
        rtp_analysis = pd.DataFrame({
            'BYE Reason': bye_reasons,
            'CaptureCallback Count': capture_callback_count.astype(int),
            'FirstRx Count': first_rx_count.astype(int),
            'Call Duration (seconds)': call_duration.astype(float),
            'Recent HealthCheck Counts': healthcheck_series,
            'SRTP Error Count': srtp_error_count.astype(int)
        })

        st.write(rtp_analysis)

        # Call Flow 분석 (확대/축소 가능)
        with st.expander("### Call Flow 분석", expanded=False):
            call_ids = df['context.callID'].dropna().unique()
            selected_call_id = st.radio("Call ID 선택", options=call_ids)
            st.write(f"선택된 Call ID: {selected_call_id}")

            # Generate sequence diagram or error message
            sequence_diagram = generate_sequence_diagram(df, selected_call_id)
            if isinstance(sequence_diagram, str):
                st.warning(sequence_diagram)
            else:
                st.graphviz_chart(sequence_diagram)

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
