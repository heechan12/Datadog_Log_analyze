import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 설정 (여기서 한 번만 호출)
st.set_page_config(
    layout="wide",
    page_title="DataDog 분석 Tool",
    page_icon=":technologist:"
)

# 사이드바 메뉴
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["상세 로그 분석 페이지", "User/버전 별 분석 페이지"],
        icons=["file-earmark-break", "bar-chart"],
        menu_icon="signpost-split",
        default_index=0,
    )

# 페이지 선택에 따라 다른 페이지 호출
if selected == "상세 로그 분석 페이지":
    from pages.log_analysis_page import log_analysis_page
    log_analysis_page()

elif selected == "User/버전 별 분석 페이지":
    from pages.user_version_analysis_page import user_version_analysis_page
    user_version_analysis_page()
