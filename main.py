import sys
from datetime import datetime, timedelta

import preprocess_data
import probability


if __name__ == '__main__':
    assert len(sys.argv) == 4
    input_csv = sys.argv[1]
    user_email = sys.argv[2]
    limit = datetime.strptime(sys.argv[3], "%d.%m.%Y")

    output_csv1 = "weekly_stats1.csv"
    output_csv2 = "weekly_stats2.csv"

    preprocess_data.get_stats(
        input_csv,
        output_csv1,
        output_csv2,
        limit,
        limit + timedelta(days=365),
        user_email
    )

    prob = probability.probability(output_csv1, output_csv2)
    print(f'Probability = {prob:.2}')
