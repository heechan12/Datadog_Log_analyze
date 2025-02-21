import streamlit as st
from streamlit_option_menu import option_menu

from utils.CONSTANTS import (
    PG_Name_RUM_ANALYSIS,
    PG_Name_USER_VERSION,
    PG_Name_HOW_TO,
    PG_Name_LOG_ANALYSIS,
)

# 페이지 설정 (여기서 한 번만 호출)
st.set_page_config(
    layout="wide", page_title="DataDog 분석 Tool", page_icon=":technologist:"
)

# 사이드바 메뉴
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=[
            PG_Name_RUM_ANALYSIS,
            PG_Name_USER_VERSION,
            PG_Name_LOG_ANALYSIS,
            PG_Name_HOW_TO,
        ],
        icons=["file-earmark-break", "bar-chart", "book"],
        menu_icon="signpost-split",
        default_index=0,
    )
    st.caption("1.3.3. 최적화")
    st.caption("지속 수정 중입니다.")

# 페이지 선택에 따라 다른 페이지 호출
if selected == PG_Name_RUM_ANALYSIS:
    from page_list.rum_analysis_page import rum_analysis_page

    rum_analysis_page()

elif selected == PG_Name_USER_VERSION:
    from page_list.user_version_analysis_page import user_version_analysis_page

    user_version_analysis_page()

elif selected == PG_Name_LOG_ANALYSIS:
    from page_list.log_analysis_page import log_analysis_page

    log_analysis_page()

elif selected == PG_Name_HOW_TO:
    from page_list.readme_page import readme_page

    readme_page()
