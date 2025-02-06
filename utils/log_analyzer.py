import pandas as pd
from utils.CONSTANTS import TB_Name_RECENT_HEALTH_CHECK

# Updated Call Duration Calculation with Debugging
def get_call_duration(df, unmatched_value='매칭되지 않음'):
    # Filter for start and stop events
    start_calls = df[df['Resource Url'].str.contains('res/ENGINE_startCall', case=False, na=False)].groupby('context.callID')['timestamp'].min()
    stop_calls = df[df['Resource Url'].str.contains('res/ENGINE_stopCall', case=False, na=False)].groupby('context.callID')['timestamp'].max()

    # Calculate duration
    call_duration = (stop_calls - start_calls).dt.total_seconds()

    # pd.NaT가 있는 경우 "분석 불가"로 대체
    call_duration = call_duration.fillna('분석 불가')

    # 매칭되지 않은 Call ID 처리
    all_call_ids = pd.Index(df['context.callID'].unique())
    duration_with_unmatched = call_duration.reindex(all_call_ids, fill_value=None)

    # 매칭되지 않은 경우 특정 값을 설정
    duration_with_unmatched = duration_with_unmatched.fillna(unmatched_value)

    # Debugging info for mismatches
    missing_starts = set(stop_calls.index) - set(start_calls.index)
    missing_stops = set(start_calls.index) - set(stop_calls.index)
    if missing_starts:
        print(f"경고: StopCall 이벤트에 매칭되지 않은 Call ID: {missing_starts}")
    if missing_stops:
        print(f"경고: StartCall 이벤트에 매칭되지 않은 Call ID: {missing_stops}")

    return duration_with_unmatched



# Optimized HealthCheck Counts per Call ID
# Fixed reindex and data conversion issues
def get_recent_healthcheck_counts(df):
    healthcheck_df = df[df['Resource Url'].str.contains('res/ENGINE_ReceiveHealthCheck', case=False, na=False)]

    if '@context.totalCount' not in df.columns:
        return pd.Series('없음', index=df['context.callID'].unique())

    # Call ID별 최근 5개 HealthCheck 추출 후 소수점 제거 및 1D 변환
    recent_counts = healthcheck_df.groupby('context.callID')['@context.totalCount'] \
                                  .apply(lambda x: ', '.join(map(lambda y: str(int(float(y))), x.sort_values(ascending=False).head(5)))) \
                                  .reindex(df['context.callID'].unique(), fill_value='없음')

    return recent_counts


# SRTP Error Count Calculation
def get_srtp_error_count(df):
    srtp_error_count = df[df['Resource Url'].str.contains('res/ENGINE_errorSrtpDepacketizer', case=False, na=False)].groupby('context.callID').size()
    return srtp_error_count

# BYE Reason Extraction
def get_bye_reasons(df):
    bye_reasons = df[df['context.method'] == 'BYE'].groupby('context.callID')['context.reasonFromLog'].first().fillna('없음')
    return bye_reasons

# Stop Holepunching Code Extraction
def get_stopholepunching_code(df):
    stop_holepunching_df = df[df['Resource Url'].str.contains('res/ENGINE_stopHolePunching', case=False, na=False)]

    if 'context.code' not in df.columns:
        return pd.Series('없음', index=df['context.callID'].unique())

    # Call ID별 가장 최근 코드를 추출하고 1D로 변환
    stop_holepunching_code = stop_holepunching_df.groupby('context.callID')['context.code'] \
                                                 .last() \
                                                 .reindex(df['context.callID'].unique(), fill_value='없음')

    return stop_holepunching_code