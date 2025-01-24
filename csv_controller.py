import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from config import SELECTED_COLS_FROM_DF


# CSV 파일 불러오기
def load_data(file) -> DataFrame :
    '''
    csv 파일 불러오기
    :param file : csv file
    :return: DataFrame(df)
    '''
    df = pd.read_csv(file)
    return df

# 열 정리
def select_columns(csv_file_data_frame) -> DataFrame :
    '''
    분석에 필요한 데이터(열) 선택
    :param csv_file_data_frame: dataframe 으로 가공된 csv 파일
    :return: DataFrame(df)
    '''
    # 필요한 열 정의
    selected_cols = SELECTED_COLS_FROM_DF

    # csv 파일에서 필요한 열 가져오기 (예외 처리 포함)
    available_cols = [col for col in selected_cols if col in csv_file_data_frame.columns]
    result_df = csv_file_data_frame[available_cols]

    return result_df