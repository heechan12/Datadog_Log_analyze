import streamlit as st
import pandas as pd
from streamlit_elements import mui, nivo, elements

from utils.CONSTANTS import PG_Name_USER_VERSION, CSV_FILE_UPLOAD, TITLE_ANALYSIS_RESULT_PER_USER_ID, \
    TITLE_ANALYSIS_RESULT_PER_APP_VERSION, TITLE_ANALYSIS_RESULT_PER_OS_VERSION


def load_and_process(file):
    df = pd.read_csv(file)
    return df

def user_version_analysis_page():
    st.title(PG_Name_USER_VERSION)

    uploaded_file = st.file_uploader(CSV_FILE_UPLOAD, type=["csv"])

    if uploaded_file is not None:
        df = load_and_process(uploaded_file)

        # 전체 열의 개수 및 중복 제거된 User Id 수 계산 및 표시
        total_rows = len(df)
        total_unique_users = df['User Id'].nunique() if 'User Id' in df.columns else 0
        summary_table = pd.DataFrame({
            '전체 행의 개수': [total_rows],
            '중복 제거된 User Id 수': [total_unique_users]
        })
        st.table(summary_table)
        # st.dataframe(summary_table)

        user_id_col, app_version_col, os_version_col = st.columns(3)

        with user_id_col :
            # User Id 별 개수 분석
            st.subheader(f":orange-background[*{TITLE_ANALYSIS_RESULT_PER_USER_ID}*]")
            if 'User Id' in df.columns:
                user_counts = df['User Id'].value_counts().reset_index()
                total_unique_users = df['User Id'].nunique()
                user_counts.columns = ['User Id', '개수']
                top_10_users = user_counts.head(10)
                st.table(top_10_users)

                with st.expander("전체 User Id 보기"):
                    st.table(user_counts)
                # st.bar_chart(user_counts.set_index('User Id')['개수'])
            else:
                st.warning("User Id 열이 없습니다.")

        with app_version_col :
            # 앱 버전 별 개수 분석
            st.subheader(f":orange-background[*{TITLE_ANALYSIS_RESULT_PER_APP_VERSION}*]")
            if 'Version' in df.columns:
                app_version_counts = df['Version'].value_counts().reset_index()
                app_version_data = [{"app_version": version} for version in app_version_counts['Version']]
                app_version_counts.columns = ['버전', '개수']
                st.table(app_version_counts)

                
                print(app_version_data)
                with elements("nivo"):
                    with mui.Box(sx={"Height":10}):
                        nivo.Pie(
                            data=app_version_data,
                        )

            else:
                st.warning("Version 열이 없습니다.")



        with os_version_col :
            st.subheader(f":orange-background[*{TITLE_ANALYSIS_RESULT_PER_OS_VERSION}*]")
            if "OS Version" in df.columns:
                os_version_counts = df['OS Version'].value_counts().reset_index()
                os_version_counts.columns = ['버전', '개수']
                st.table(os_version_counts)
                # st.bar_chart(version_counts.set_index('버전')['개수'])
            else:
                st.warning("OS Version 열이 없습니다.")



if __name__ == "__main__":
    user_version_analysis_page()
