import streamlit as st
import pandas as pd

def load_and_process(file):
    df = pd.read_csv(file)
    return df

def user_version_analysis():
    st.title("User/버전 분석 페이지")

    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file is not None:
        df = load_and_process(uploaded_file)

        # User Id 별 개수 분석
        if 'User Id' in df.columns:
            user_counts = df['User Id'].value_counts().reset_index()
            user_counts.columns = ['User Id', '개수']
            st.subheader("User Id 별 개수")
            st.table(user_counts)
            st.bar_chart(user_counts.set_index('User Id')['개수'])
        else:
            st.warning("User Id 열이 없습니다.")

        # 버전 별 개수 분석
        if 'Version' in df.columns:
            version_counts = df['Version'].value_counts().reset_index()
            version_counts.columns = ['버전', '개수']
            st.subheader("버전 별 개수")
            st.table(version_counts)
            st.bar_chart(version_counts.set_index('버전')['개수'])
        else:
            st.warning("Version 열이 없습니다.")
