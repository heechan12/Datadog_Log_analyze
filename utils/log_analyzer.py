import pandas as pd
from utils.CONSTANTS import TB_Name_RECENT_HEALTH_CHECK

# TODO : CALL ID 별로 REGISTER 목적의 CAll ID 인지, INVITE 목적의 CAll ID 인지 구분

# Call ID 기준으로 INVITE 가 포함되어 있는지, REGISTER 가 포함되어 있는지 확인
# if INVITE 가 포함되어 있으면 return call 
# if REGISTER 가 포함되어 있으면 return register 
# if 둘 다 포함되어 있으면 return both
# 그 외 return none
# def get_call_id_info(df):
#     # 각 callID에 대해 INVITE와 REGISTER 메시지 포함 여부 확인
#     call_info = df.groupby('context.callID')['context.method'].apply(lambda x: {
#         'INVITE': 'INVITE' in x.values,
#         'REGISTER': 'REGISTER' in x.values
#     })

#     # 결과를 저장할 Series 생성
#     result = pd.Series(index=call_info.index)

#     for call_id, info in call_info.items():
#         if isinstance(info, dict):  # info가 딕셔너리인지 확인
#             if info['INVITE'] and info['REGISTER']:
#                 result[call_id] = 'both'
#             elif info['INVITE']:
#                 result[call_id] = 'call'
#             elif info['REGISTER']:
#                 result[call_id] = 'register'
#             else:
#                 result[call_id] = 'none'
#         else:
#             result[call_id] = 'none'  # info가 딕셔너리가 아닐 경우 처리

#     return result


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

# Call End Reason Extraction
# cursor ai
def get_call_end_reasons(df):
    # 각 통화 종료 유형별로 데이터 추출
    cancel_calls = df[df['context.method'] == 'CANCEL'].groupby('context.callID')['timestamp'].first().dt.tz_localize(None)
    decline_calls = df[df['Resource Url'].str.contains('603 Decline', na=False)].groupby('context.callID')['timestamp'].first().dt.tz_localize(None)
    bye_calls = df[df['context.method'] == 'BYE'].groupby('context.callID').agg({
        'timestamp': 'first',
        'context.reasonFromLog': 'first'
    })
    bye_calls['timestamp'] = bye_calls['timestamp'].dt.tz_localize(None)  # BYE 타임스탬프도 tz-naive로 변환

    # 결과를 저장할 Series 생성
    all_call_ids = df['context.callID'].unique()
    end_reasons = pd.Series(index=all_call_ids, data='알 수 없음')

    # 각 종료 유형별로 처리 (시간순으로 가장 먼저 발생한 이벤트를 종료 원인으로 선택)
    for call_id in all_call_ids:
        reason = '알 수 없음'
        reason_time = pd.Timestamp.max

        # CANCEL 체크
        if call_id in cancel_calls:
            cancel_time = cancel_calls[call_id]
            if cancel_time < reason_time:
                reason = 'CANCEL'
                reason_time = cancel_time

        # 603 Decline 체크
        if call_id in decline_calls:
            decline_time = decline_calls[call_id]
            if decline_time < reason_time:
                reason = 'DECLINED'
                reason_time = decline_time

        # BYE 체크
        if call_id in bye_calls.index:
            bye_time = bye_calls.loc[call_id, 'timestamp']
            if bye_time < reason_time:
                reason = f"BYE ({bye_calls.loc[call_id, 'context.reasonFromLog']})"
                reason_time = bye_time

        end_reasons[call_id] = reason

    return end_reasons

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