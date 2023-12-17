from datetime import datetime, timedelta
import os

import preprocess_data
import probability


def users_probability(
    input_csv : str,
    user_emails : list[str],
    start_date1 : datetime,
    end_date1 : datetime,
    start_date2 : datetime,
    end_date2 : datetime
):
    probabilities = []

    for user_email in user_emails:
        output_csv1 = f"weekly_stats_1_{user_email}.csv"
        output_csv2 = f"weekly_stats_2_{user_email}.csv"

        preprocess_data.get_stats(
            input_csv,
            output_csv1,
            output_csv2,
            start_date1, end_date1,
            start_date2, end_date2,
            user_email
        )

        probabilities.append(probability.probability(output_csv1, output_csv2))
        os.remove(output_csv1)
        os.remove(output_csv2)

    return probabilities
