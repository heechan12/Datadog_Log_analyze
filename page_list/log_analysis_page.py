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
    # 메시지를 "|" 기준으로 분리하기
    if df["Message"] is not None:
        messages = df["Message"].str.split("|", expand=True)

        # 각 메시지에서 키-값 쌍을 "=" 기준으로 분리하여 열 이름으로 사용
        for i in range(messages.shape[1]):
            if messages[i].isnull().all():  # 모든 값이 NaN인 경우 건너뛰기
                continue
            key_value_pairs = messages[i].str.split("=", n=1, expand=True)
            if key_value_pairs.shape[1] == 2:  # 키-값 쌍이 있는 경우
                key = key_value_pairs[0].str.strip()  # 키에서 공백 제거
                value = key_value_pairs[1].str.strip()  # 값에서 공백 제거
                # DataFrame에 추가
                df[key] = value

    else:
        st.toast(f"⚠️ 첨부된 파일에 Message 열이 없습니다.")

    return df


def display_table(df):
    st.subheader(f":orange-background[*{TITLE_LOG_ANALYSIS_TABLE}*]")

    log_table = pd.DataFrame(df)

    st.dataframe(log_table)


def log_analysis_page():
    st.title(PG_Name_LOG_ANALYSIS)

    uploaded_file = st.file_uploader(CSV_FILE_UPLOAD, type=["csv"])

    if uploaded_file is not None:

        df = load_and_process(uploaded_file)
        df = separate_message(df)

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
                    "Message",
                    "pid",
                    "filename",
                    "fromCtn",
                    "toCtn",
                    "fromTag",
                    "toTag",
                    "date",
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
            st.subheader(f":orange-background[*{TITLE_FILTERED_DATA}*]")
            st.write(filtered_df[columns_to_show])

        # NOTE : Log 분석 페이지 기본 테이블
        with st.container(border=True):
            st.subheader(f":orange-background[*{TITLE_DEFAULT_DATA}*]")
            with st.expander("펼치기", expanded=False):
                st.write(df)


if __name__ == "__main__":
    log_analysis_page()
