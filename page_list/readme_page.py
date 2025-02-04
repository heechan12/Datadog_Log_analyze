import streamlit as st

def readme_page() :
    # Title
    # st.markdown("# 사용법")
    st.header("사용법")

    # Subtitle - 상세 로그 분석 페이지
    st.markdown("### :blue-background[*상세 로그 분석 페이지*] ")
    st.markdown("#### 1. Datadog 에서 csv 파일 다운로드")
    st.image("assets/log_analysis_page_readme.png")
    st.markdown("#### 2. 상세 로그 분석 페이지에 csv 파일 업로드")
    st.markdown("#### 3. 로그 분석")
    st.image("assets/log_analysis_detail_readme.png")
    # st.markdown(":warning: :red[**다운로드 전 필요한 column 을 미리 추가해주세요**]")
    # st.text("RTP Timeout 이 발생한 Session 의 자료를 다운 받아주세요")

    st.divider()

    # Subtitle - User/버전 별 분석 페이지
    st.markdown("### :blue-background[*User/버전 별 분석 페이지*] ")
    st.markdown(":warning: :red[**다운로드 전 usr.id, app version column을 미리 추가해주세요**]")
    st.markdown("#### 1. Datadog 에서 csv 파일 다운로드")
    st.image("assets/user_version_analysis_page_readme.png")
    st.markdown("#### 2. 상세 로그 분석 페이지에 csv 파일 업로드 및 통계 확인")

    # st.markdown(
    #     '''
    #
    #
    #     ## :blue-background[*User/버전 별 분석 페이지*]
    #     RTP Timeout 분석을 위한 용도로
    #     (@context.method:BYE @context.reason:RTP*)
    #     '''
    # )

if __name__ == "__main__" :
    readme_page()