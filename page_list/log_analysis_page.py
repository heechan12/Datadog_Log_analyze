import streamlit as st
import pandas as pd
from datetime import timedelta

from utils.CONSTANTS import *


def load_and_process(file):
    # CSV 파일 읽고 시간 변환 및 URL 처리
    df = pd.read_csv(file)
    df["Date"] = (
        pd.to_datetime(df["Date"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors="coerce")
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Seoul")
    )
    return df


def separate_message(df):
    # TODO : 메시지를 "|" 기준으로 분리하기
    # "date=2025-02-20 23:59:18.423|serverType=03|pid=3385231|logLevel=INFO|filename=thread/ThreadToIMSServerSender.h|line=198|callId=thhsdcyb-0-1-a009vCZsCDeMlVvsgik@ghgpkkklkjm|errorCode=40810300|fromCtn=[CTN_REMOVED]|toCtn=[CTN_REMOVED]|fromTag=kmnham6A0E0957793774942665|toTag=ONEAT1740063558189072170833852316cb1a5c3|calling=outGoing|method=408 Request Timeout|messageType=REQ|from=SIGNAL-172.31.178.112:5060|to=CSCF-10.113.127.14:5060|ip=10.113.127.14|port=5060|message=\rSIP/2.0 408 Request Timeout\rVia: SIP/2.0/UDP 10.113.127.14:5060;[BRANCH_REMOVED] <[CTN_REMOVED]@lte-lguplus.co.kr>;tag=kmnham6A0E0957793774942665\rTo: <[CTN_REMOVED];phone-context=lte-lguplus.co.kr>;tag=ONEAT1740063558189072170833852316cb1a5c3\rCall-ID: thhsdcyb-0-1-a009vCZsCDeMlVvsgik@ghgpkkklkjm\rCSeq: 9203 INVITE\rContact: <sip:172.31.178.112:5060>;+g.3gpp.icsi-ref=""urn%3Aurn-7%3A3gpp-service.ims.icsi.mmtel""\rMax-Forwards: 70\rContent-Length: 0\rReason: SIP;cause=99719408;text=""No Response 180 Ring""\r\r"
    # date, serverType, pid, logLevel, filename, line, callId, errorCode 등 "=" 앞에 있는 것으로 "열 이름"화 하기
    return


def display_table(df):
    st.subheader(f":orange-background[*{TITLE_LOG_ANALYSIS_TABLE}*]")

    log_table = pd.DataFrame(df)

    st.dataframe(log_table)


def log_analysis_page():
    st.title(PG_Name_LOG_ANALYSIS)

    uploaded_file = st.file_uploader(CSV_FILE_UPLOAD, type=["csv"])

    if uploaded_file is not None:

        df = load_and_process(uploaded_file)

        # NOTE : Log 분석 페이지 사이드 바 영역
        st.sidebar.header("열 선택")
        columns_to_show = st.sidebar.multiselect(
            "보고 싶은 열을 선택하세요",
            df.columns.tolist(),
            default=[
                col
                for col in df.columns
                if col
                not in [
                    "Host",
                    "Service",
                ]
            ],
        )

        # 필터링 옵션
        st.sidebar.header("필터")
        filter_condition = st.sidebar.radio("필터 조건", ["AND", "OR"])
        filtered_df = df.copy()
        filters = []

        for col in columns_to_show:
            unique_values = df[col].dropna().unique()
            if len(unique_values) > 0 and df[col].dtype == "object":
                selected_values = st.sidebar.multiselect(f"{col} 선택", unique_values)
                if selected_values:
                    if filter_condition == "AND":
                        filters.append(filtered_df[col].isin(selected_values))
                    else:
                        filters.append(filtered_df[col].isin(selected_values))
        if filters:
            condition = (
                pd.concat(filters, axis=1).all(axis=1)
                if filter_condition == "AND"
                else pd.concat(filters, axis=1).any(axis=1)
            )
            filtered_df = filtered_df[condition]

        # NOTE : Log 분석 페이지 필터링 테이브
        with st.container(border=True):
            st.write(filtered_df)

        # NOTE : Log 분석 페이지 기본 테이블
        with st.container(border=True):
            # display_table(df)
            st.write(df)


if __name__ == "__main__":
    log_analysis_page()
