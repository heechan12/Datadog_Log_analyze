import streamlit as st

# Title
st.markdown("# 사용법")

# Subtitle - 메인 페이지
st.markdown("## :blue-background[*상세 로그 분석 페이지*] ")
st.markdown("### 1. Datadog 에서 csv 파일 다운로드")
st.markdown(":warning: :red[**다운로드 전 필요한 column 을 미리 추가해주세요**]")
st.text("RTP Timeout 이 발생한 Session 의 자료를 다운 받아주세요")

st.markdown(
    '''
    
    
    ## :blue-background[*User/버전 별 분석 페이지*] 
    RTP Timeout 분석을 위한 용도로
    (@context.method:BYE @context.reason:RTP*) 
    '''
)