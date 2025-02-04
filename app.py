import streamlit as st
from streamlit.source_util import page_icon_and_name
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
        menu_title="메뉴 선택",
        options=["메인 페이지", "User/버전 분석 페이지"],
        icons=["house", "bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

# 페이지 선택에 따라 다른 페이지 호출
if selected == "메인 페이지":
    from main_page import main_page
    main_page()

elif selected == "User/버전 분석 페이지":
    from user_version_analysis import user_version_analysis
    user_version_analysis()
