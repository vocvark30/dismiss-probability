# Входные данные:
# - 2 .csv файла с фичами за 2 периода
# - фичи:
# sent_msgs_count, answered_msgs, out_msgs_text_len, out_workday_msgs, recv_sent_ratio, unanswered_qstn_msgs, sent_sentiment_score, received_sentiment_score
#   - Количество отправленных сообщений за период;
#   - Количество сообщений, на которые произведен ответ;
#   - Количество символов текста в исходящих сообщениях;
#   - Количество сообщений, отправленных вне рамок рабочего дня;
#   - Соотношение количества полученных и отправленных сообщений;
#   - Количество входящих сообщений, имеющих вопросительные	знаки в
#       тексте, но на которые не был направлен ответ.
#   - Оценка "позитивности" отправленных сообщений
#   - Оценка "позитивности" полученных сообщений

# Выходные данные: число из [0, 1] - вероятность

import pandas as pd
import numpy as np
import math
import numpy as np

import consts

def replace_outliers_with_mean_no_outliers(df, k=2):
    cleaned_df = df.copy()
    for column in cleaned_df.columns:
        # Вычисление межквартильного размаха
        Q1, Q3 = np.percentile(cleaned_df[column], [25, 75])
        IQR = Q3 - Q1

        lower_bound = Q1 - k * IQR
        upper_bound = Q3 + k * IQR

        is_outlier = (cleaned_df[column] < lower_bound) | (cleaned_df[column] > upper_bound)

        # Замена выбросов средним значением без учета выбросов
        mean_value_no_outliers = cleaned_df.loc[~is_outlier, column].mean()
        cleaned_df[column] = cleaned_df[column].mask(is_outlier, mean_value_no_outliers)

    return cleaned_df

# Функция преобразования x ~ N(0, 1) в величину отклонения
def weighted_deviation(x):
    alpha = 0.16
    return alpha * x**2 * (1 if x > 0 else -1)

# Смещенная сигмоида
def sigmoid(x):
    return 1 / (1 + math.exp(-12 * x + 3))


def probability(csv_name1, csv_name2, debug=False):
    data1 = pd.read_csv(csv_name1).apply(pd.to_numeric, errors='coerce')
    data2 = pd.read_csv(csv_name2).apply(pd.to_numeric, errors='coerce')

    df1 = replace_outliers_with_mean_no_outliers(data1)
    df2 = replace_outliers_with_mean_no_outliers(data2)

    normal_deviation = (df2.mean() - df1.mean()) / df1.std()

    normal_deviation.replace([np.inf, -np.inf], np.nan, inplace=True)
    normal_deviation = normal_deviation.fillna(0)

    if debug:
        print(f'data 1:\n{df1}\n\ndata 2:\n{df2}')
        print(f'csv 1 means:\n{df1.mean()}\n\ncsv 2 means:\n{df2.mean()}')
        print(f'\nnormal_deviation:\n{normal_deviation}\n')

    final_statistics = 0.0

    for name, k in consts.coefficients.items():
        f_x = weighted_deviation(normal_deviation[name])
        final_statistics += f_x * k

        if debug:
            print(f'{name} : {f_x}')

    if debug:
        print(f'final statistics = {final_statistics}')

    # Чем больше значение статистики, тем меньше вероятность
    return sigmoid(-final_statistics)
