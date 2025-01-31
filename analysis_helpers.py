import pandas as pd


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
    healthcheck_df = df[df['Resource Url'].str.contains('res/ENGINE_ReceiveHealthCheck', case=False, na=False)]

    # Group and get recent counts
    recent_counts = healthcheck_df.groupby('context.callID').apply(
        lambda x: ', '.join(map(str, x.sort_values(by='timestamp', ascending=False).head(5)['@context.totalCount'].tolist()))
    )

    # Reindex to match all Call IDs and fill missing values with '없음'
    recent_counts = recent_counts.reindex(df['context.callID'].unique(), fill_value='없음')

    # Ensure it returns a valid pandas Series with matching index
    return recent_counts.reset_index(drop=True).astype(str)



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