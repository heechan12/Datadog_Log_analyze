import streamlit as st
import pandas as pd
from sequence_diagram import generate_plantuml_sequence, render_plantuml
from analysis_helpers import get_call_duration, get_recent_healthcheck_counts, get_srtp_error_count, get_bye_reasons

def load_and_process(file):
    df = pd.read_csv(file)
    # UTC 시간을 KST(한국 시간)으로 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['Resource Url'] = df['Resource Url'].str.replace('https://aicall-lgu.com/', '', regex=False)
    df['Resource Url'] = df['Resource Url'].str.strip()  # 공백 제거
    return df

def main_page():
    st.title("메인 페이지 - CSV 파일 분석 도구")

    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        df = load_and_process(uploaded_file)

        # RTP Timeout 분석을 위해 Call ID가 필요한 경우만 사용
        call_id_filtered_df = df.dropna(subset=['context.callID'])

        # RTP Timeout 분석
        st.write("### 통화 종료(BYE) 분석")
        capture_callback_count = call_id_filtered_df[call_id_filtered_df['context.method'] == 'CaptureCallback'].groupby('context.callID').size().reindex(
            call_id_filtered_df['context.callID'].unique(), fill_value=0)
        first_rx_count = call_id_filtered_df[call_id_filtered_df['Resource Url'].str.contains('firstRx', na=False)].groupby(
            'context.callID').size().reindex(call_id_filtered_df['context.callID'].unique(), fill_value=0)
        call_duration = get_call_duration(call_id_filtered_df).fillna(0)

        # 수정된 HealthCheck Counts 재정렬
        healthcheck_counts = get_recent_healthcheck_counts(call_id_filtered_df)
        healthcheck_series = healthcheck_counts.reindex(call_duration.index, fill_value='없음')

        srtp_error_count = get_srtp_error_count(call_id_filtered_df).reindex(call_duration.index, fill_value=0)
        bye_reasons = get_bye_reasons(call_id_filtered_df).reindex(call_duration.index).fillna('없음')

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
        with st.expander("### Call Flow 분석 (시퀀스 다이어그램)", expanded=False):
            call_ids = call_id_filtered_df['context.callID'].dropna().unique()
            selected_call_id = st.radio("Call ID 선택", options=call_ids)
            st.write(f"선택된 Call ID: {selected_call_id}")

            # Generate sequence diagram
            plantuml_code = generate_plantuml_sequence(call_id_filtered_df, selected_call_id)
            diagram_content = render_plantuml(plantuml_code)

            # Display the contents of sequence_diagram.txt
            st.text_area("시퀀스 다이어그램 내용 (sequence_diagram.txt)", diagram_content, height=400)

        # 사이드바에서 원하는 열 선택
        st.sidebar.header("열 선택")
        columns_to_show = st.sidebar.multiselect(
            "보고 싶은 열을 선택하세요",
            df.columns.tolist(),
            default=[col for col in df.columns if col not in ['has_replay', 'status', 'timestamp', 'View name', 'Resource Duration', 'Resource Size', 'Resource Status']]
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
            if filter_condition == "AND":
                filtered_df = filtered_df.loc[pd.concat(filters, axis=1).all(axis=1)]
            else:
                filtered_df = filtered_df.loc[pd.concat(filters, axis=1).any(axis=1)]

        st.write("### 필터링된 데이터")
        st.write(filtered_df[columns_to_show])

        st.write("### 선택한 열 데이터")
        st.write(df[columns_to_show])

if __name__ == "__main__":
    main_page()
