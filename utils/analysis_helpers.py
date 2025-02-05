import pandas as pd

from utils.CONSTANTS import TB_Name_RECENT_HEALTH_CHECK


# Updated Call Duration Calculation with Debugging
def get_call_duration(df):
    # Filter for start and stop events
    start_calls = \
    df[df['Resource Url'].str.contains('res/ENGINE_startCall', case=False, na=False)].groupby('context.callID')[
        'timestamp'].min()
    stop_calls = \
    df[df['Resource Url'].str.contains('res/ENGINE_stopCall', case=False, na=False)].groupby('context.callID')[
        'timestamp'].max()

    # Calculate duration
    call_duration = (stop_calls - start_calls).dt.total_seconds()
    call_duration = call_duration.fillna(0)  # Handle cases where either start or stop is missing

    # Debugging info for mismatches
    missing_starts = set(stop_calls.index) - set(start_calls.index)
    missing_stops = set(start_calls.index) - set(stop_calls.index)
    if missing_starts:
        print(f"경고: StopCall 이벤트에 매칭되지 않은 Call ID: {missing_starts}")
    if missing_stops:
        print(f"경고: StartCall 이벤트에 매칭되지 않은 Call ID: {missing_stops}")

    return call_duration


# Optimized HealthCheck Counts per Call ID
# Fixed reindex and data conversion issue
def get_recent_healthcheck_counts(df):
    # HealthCheck 로그 필터링
    healthcheck_df = df[df['Resource Url'].str.contains('res/ENGINE_ReceiveHealthCheck', case=False, na=False)]

    # 열이 존재하는지 확인
    if '@context.totalCount' not in df.columns:
        return pd.Series(['없음'] * len(df['context.callID']), index=df.index, name=TB_Name_RECENT_HEALTH_CHECK)

    # Call ID별 최근 5개 HealthCheck 데이터 추출 (소수점 제거)
    recent_counts = healthcheck_df.groupby('context.callID').apply(
        lambda x: ', '.join(map(lambda y: str(int(float(y))),
                                x.sort_values(by='timestamp', ascending=False).head(5)['@context.totalCount'].tolist()))
    )

    return recent_counts


# SRTP Error Count Calculation
def get_srtp_error_count(df):
    srtp_error_count = df[
        df['Resource Url'].str.contains('res/ENGINE_errorSrtpDepacketizer', case=False, na=False)].groupby(
        'context.callID').size()
    return srtp_error_count


# BYE Reason Extraction
def get_bye_reasons(df):
    bye_reasons = df[df['context.method'] == 'BYE'].groupby('context.callID')['context.reasonFromLog'].first().fillna(
        '없음')
    return bye_reasons