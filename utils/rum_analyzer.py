import pandas as pd
import streamlit as st
import time
from utils.CONSTANTS import TB_Name_RECENT_HEALTH_CHECK


# TODO : CALL ID 별로 REGISTER 목적의 CAll ID 인지, INVITE 목적의 CAll ID 인지 구분
# CHECKLIST : 간단하게 기존 함수들처럼 REGISTER, INVITE 포함 여부로 판단해도 될듯?
def classify_call_id_type(df):
    # 만약 call id 에 thhsdcyb 가 포함되어 있으면 -> 착신 통화
    # 아니면 ->
    #   context.method 에 INVITE, BYE, DECLINE, UPDATE 등이 있으면 발신 통화
    #   context.method 에 REGISTER 가 있으면 REGISTER
    # Pandas 로 분리
    call_type_register = df[
        df["context.method"].str.contains("REGISTER", case=False, na=False)
    ].groupby("context.callID")

    return


# NOTE : 단순 테스트 용도
# FIXME : 누락되는 케이스가 있음
def classify_sessions(df):
    """
    callUniqueId를 기준으로 통화 세션을 분류하는 함수.
    각 callUniqueId의 시작 시간과 종료 시간 사이의 로그를 동일한 세션으로 할당.

    :param df: DataFrame, 로그 데이터
    :return: DataFrame, 세션 정보가 추가된 데이터
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )  # timestamp 컬럼을 datetime 형식으로 변환
    df = df.sort_values(by=["timestamp"])  # 시간 순으로 정렬

    session_id = 0  # 세션 ID 초기화
    df["session_id"] = None  # 새로운 세션 ID 컬럼 추가

    unique_ids = df["context.callUniqueId"].dropna().unique()

    for call_id in unique_ids:
        call_logs = df[df["context.callUniqueId"] == call_id]
        if call_logs.empty:
            continue

        start_time = call_logs["timestamp"].min()
        end_time = call_logs["timestamp"].max()

        # 해당 callUniqueId의 시작-종료 시간 사이에 존재하는 모든 로그에 같은 session_id 할당
        df.loc[
            (df["timestamp"] >= start_time) & (df["timestamp"] <= end_time),
            "session_id",
        ] = session_id
        session_id += 1  # 다음 세션을 위해 ID 증가

    df["session_id"] = df["session_id"].astype("Int64")  # 세션 ID 정수형 변환
    df.to_csv("assets/temp.csv")
    print("저장 완료")
    return df


# TODO : Audio Session Routed 분석 추가


def get_call_duration(df, unmatched_value="매칭되지 않음"):
    """
    call id 별 ENGINE_startCall ~ ENGINE_stopCall 까지의 시간 측정
    """
    start_calls = (
        df[
            df["Resource Url"].str.contains(
                "res/ENGINE_startCall", case=False, na=False
            )
        ]
        .groupby("context.callID")["timestamp"]
        .min()
    )
    stop_calls = (
        df[df["Resource Url"].str.contains("res/ENGINE_stopCall", case=False, na=False)]
        .groupby("context.callID")["timestamp"]
        .max()
    )

    call_duration = (stop_calls - start_calls).dt.total_seconds()

    # pd.NaT가 있는 경우 "분석 불가"로 대체
    call_duration = call_duration.fillna("분석 불가")

    # 매칭되지 않은 Call ID 처리
    all_call_ids = pd.Index(df["context.callID"].unique())
    duration_with_unmatched = call_duration.reindex(all_call_ids, fill_value=None)

    # 매칭되지 않은 경우 특정 값을 설정
    duration_with_unmatched = duration_with_unmatched.fillna(unmatched_value)

    # 매칭되지 않은 부분 디버깅 용도
    missing_starts = set(stop_calls.index) - set(start_calls.index)
    missing_stops = set(start_calls.index) - set(stop_calls.index)
    if missing_starts:
        st.toast(f"⚠️ StopCall 이벤트에 매칭되지 않은 Call ID: {missing_starts}")
        time.sleep(0.5)
    if missing_stops:
        st.toast(f"⚠️ StartCall 이벤트에 매칭되지 않은 Call ID: {missing_stops}")
        time.sleep(0.5)

    return duration_with_unmatched


def get_capture_callback_count(df):
    """
    CaptureCallback 메시지의 수를 각 callID 별로 계산합니다.
    :param df:
    :return: call id 별 capture callback 수
    """
    capture_callback_count = (
        df[df["context.method"] == "CaptureCallback"].groupby("context.callID").size()
    )
    return capture_callback_count


def get_recent_healthcheck_counts(df):
    """

    :param df:
    :return: call id 별 healthcheck 수
    """
    healthcheck_df = df[
        df["Resource Url"].str.contains(
            "res/ENGINE_ReceiveHealthCheck", case=False, na=False
        )
    ]

    if "@context.totalCount" not in df.columns:
        return pd.Series("없음", index=df["context.callID"].unique())

    # Call ID별 최근 5개 HealthCheck 추출 후 소수점 제거 및 1D 변환
    recent_counts = (
        healthcheck_df.groupby("context.callID")["@context.totalCount"]
        .apply(
            lambda x: ", ".join(
                map(
                    lambda y: str(int(float(y))), x.sort_values(ascending=False).head(5)
                )
            )
        )
        .reindex(df["context.callID"].unique(), fill_value="없음")
    )

    return recent_counts


def get_srtp_error_count(df):
    """

    :param df:
    :return: call id 별 SRTP Error Count 수
    """
    srtp_error_count = (
        df[
            df["Resource Url"].str.contains(
                "res/ENGINE_errorSrtpDepacketizer", case=False, na=False
            )
        ]
        .groupby("context.callID")
        .size()
    )
    return srtp_error_count


def get_call_end_reasons(df):
    """

    :param df:
    :return: call id 별 통화 종료 사유(CANCEL, DECLINE, BYE)
    """
    # 각 통화 종료 유형별로 데이터 추출
    cancel_calls = (
        df[df["context.method"] == "CANCEL"]
        .groupby("context.callID")
        .agg({"timestamp": "first", "context.reasonFromLog": "first"})
    )
    cancel_calls["timestamp"] = cancel_calls["timestamp"].dt.tz_localize(None)

    decline_calls = (
        df[df["context.method"] == "DECLINED"]
        .groupby("context.callID")["timestamp"]
        .first()
        .dt.tz_localize(None)
    )
    decline_calls = (
        df[df["context.method"] == "DECLINED"]
        .groupby("context.callID")
        .agg({"timestamp": "first", "context.reasonFromLog": "first"})
    )
    decline_calls["timestamp"] = decline_calls["timestamp"].dt.tz_localize(None)

    bye_calls = (
        df[df["context.method"] == "BYE"]
        .groupby("context.callID")
        .agg({"timestamp": "first", "context.reasonFromLog": "first"})
    )
    bye_calls["timestamp"] = bye_calls["timestamp"].dt.tz_localize(
        None
    )  # BYE 타임스탬프도 tz-naive로 변환

    # 결과를 저장할 Series 생성
    all_call_ids = df["context.callID"].unique()
    end_reasons = pd.Series(index=all_call_ids, data="알 수 없음")

    # 각 종료 유형별로 처리 (시간순으로 가장 먼저 발생한 이벤트를 종료 원인으로 선택)
    for call_id in all_call_ids:
        reason = "알 수 없음"
        reason_time = pd.Timestamp.max

        # CANCEL 체크
        # DONE : BYE 처럼 reason 도  같이 보여주기
        if call_id in cancel_calls.index:
            cancel_time = cancel_calls.loc[call_id, "timestamp"]
            if cancel_time < reason_time:
                reason = (
                    f"CANCEL ({cancel_calls.loc[call_id, 'context.reasonFromLog']})"
                )
                reason_time = cancel_time

        # 603 Decline 체크
        # DONE : BYE 처럼 reason 도  같이 보여주기
        if call_id in decline_calls.index:
            decline_time = decline_calls.loc[call_id, "timestamp"]
            if decline_time < reason_time:
                reason = "DECLINED"
                reason = f"603 DECLINED ({decline_calls.loc[call_id, 'context.reasonFromLog']})"
                reason_time = decline_time

        # BYE 체크
        if call_id in bye_calls.index:
            bye_time = bye_calls.loc[call_id, "timestamp"]
            if bye_time < reason_time:
                reason = f"BYE ({bye_calls.loc[call_id, 'context.reasonFromLog']})"
                reason_time = bye_time

        end_reasons[call_id] = reason

    return end_reasons


def get_bye_reasons(df):
    """

    :param df:
    :return: BYE Reason
    """
    bye_reasons = (
        df[df["context.method"] == "BYE"]
        .groupby("context.callID")["context.reasonFromLog"]
        .first()
        .fillna("없음")
    )
    return bye_reasons


def get_stopholepunching_code(df):
    """

    :param df:
    :return: call id 별 stop holepunching code
    """
    stop_holepunching_df = df[
        df["Resource Url"].str.contains(
            "res/ENGINE_stopHolePunching", case=False, na=False
        )
    ]

    if "context.code" not in df.columns:
        return pd.Series("없음", index=df["context.callID"].unique())

    # Call ID별 가장 최근 코드를 추출하고 1D로 변환
    stop_holepunching_code = (
        stop_holepunching_df.groupby("context.callID")["context.code"]
        .last()
        .reindex(df["context.callID"].unique(), fill_value="없음")
    )

    return stop_holepunching_code


def get_call_start_time(df):
    """가장 먼저 체크되는 INVITE 메시지의 시간

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """
    call_start_time = df[df["context.method"] == "INVITE"].groupby("context.callID")[
        "timestamp"
    ]

    return call_start_time


def get_first_rx_count(df):
    """firstRx 개수 확인

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """

    first_rx_count = df[df["Resource Url"].str.contains("firstRx", na=False)].groupby(
        "context.callID"
    )

    return first_rx_count


def unify_call_id(df):
    """
    callId, callID, callUniqueId 등 다양한 Call ID 필드를 'context.callID'로 통합합니다.
    """
    # 통합할 Call ID 열 목록
    id_cols = ['context.callID', 'context.callId', 'context.callUniqueId']
    # DataFrame에 실제로 존재하는 Call ID 열만 필터링
    present_id_cols = [col for col in id_cols if col in df.columns]

    # 통합할 Call ID 열이 없으면 원본 DataFrame을 그대로 반환
    if not present_id_cols:
        return df

    # 존재하는 Call ID 열들을 통합(coalesce)하여 하나의 시리즈로 만듭니다.
    # present_id_cols의 첫 번째 열을 기준으로 시작합니다.
    unified_series = df[present_id_cols[0]].copy()
    # 나머지 열들을 순회하며 NaN 값을 채워나갑니다.
    for i in range(1, len(present_id_cols)):
        unified_series = unified_series.fillna(df[present_id_cols[i]])

    # 통합된 시리즈를 표준 'context.callID' 열에 할당합니다.
    # 이렇게 하면 이후의 모든 분석 함수가 일관된 필드를 참조할 수 있습니다.
    df['context.callID'] = unified_series
        
    return df
