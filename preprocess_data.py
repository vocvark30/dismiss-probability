import csv
from datetime import datetime, time, timedelta

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

def load_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
    return reader

def save_csv(file_path, stats_list):
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "sent_msgs_count",
            "answered_msgs",
            "out_msgs_text_len",
            "out_workday_msgs",
            "recv_sent_ratio",
            "unanswered_qstn_msgs",
            "sent_sentiment_score",
            "received_sentiment_score",
            ])

        for week_start, week_end, period_stats in stats_list:
            # writer.writerow([week_start, week_end] + list(period_stats.values()))
            writer.writerow(list(period_stats.values()))


def get_period_start_end_dates(data):
    start_date = min(datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S").date() for row in data)
    end_date = max(datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S").date() for row in data)

    current_date = start_date
    period_ranges = []
    while current_date <= end_date:
        period_start = current_date
        period_end = current_date + timedelta(days=6)
        period_ranges.append((period_start, period_end))
        current_date = period_end + timedelta(days=1)

    return period_ranges


def get_sentiment_score(message):
    result = model.predict([message], k=2)[0]

    val1 = result["negative"] if "negative" in result else 0.0
    val2 = result["positive"] if "positive" in result else 0.0
    val3 = result["neutral"] if "neutral" in result else 0.0
    val4 = result["speech"] if "speech" in result else 0.0

    return -val1 + val2 + 0.2 * val3 + 0.2 * val4


def weekly_stats(data, period_start, period_end, user_email):
    stats = {
        "sent_msgs_count": 0,
        "answered_msgs": 0,
        "out_msgs_text_len": 0,
        "out_workday_msgs": 0,
        "recv_sent_ratio": 0,
        "unanswered_qstn_msgs": 0,
        "sent_sentiment_score" : 0.0,
        "received_sentiment_score" : 0.0,
    }

    workday_start = time(8, 0)
    workday_end = time(17, 0)
    answered_subjects = set()
    total_count = 0

    for row in data:
        date_obj = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S")
        if period_start <= date_obj.date() <= period_end:
            total_count += 1
            if row["From"] == user_email:
                stats["sent_msgs_count"] += 1
                stats["out_msgs_text_len"] += len(row["Body"])
                if not (workday_start <= date_obj.time() <= workday_end) or date_obj.weekday() >= 5:
                    stats["out_workday_msgs"] += 1

                if row["Subject"].lower().startswith("re:"):
                    answered_subjects.add(row["Subject"][4:].strip())
                stats["sent_sentiment_score"] += get_sentiment_score(row["Body"])
            elif row["To"] == user_email:
                stats["received_sentiment_score"] += get_sentiment_score(row["Body"])


    stats["answered_msgs"] = len(answered_subjects)

    if stats["sent_msgs_count"] != 0:
        stats["recv_sent_ratio"] = (total_count - stats["sent_msgs_count"]) / stats["sent_msgs_count"]

    for row in data:
        if row["To"] == user_email:
            date_obj = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S")
            if period_start <= date_obj.date() <= period_end:
                if "?" in row["Body"] and row["Subject"] not in answered_subjects:
                    stats["unanswered_qstn_msgs"] += 1

    return stats

def get_stats(file_path, output_csv1, output_csv2, date1, date2, user_email):
    data = load_csv(file_path)
    period_ranges = get_period_start_end_dates(data)

    weekly_stats_list1 = []
    weekly_stats_list2 = []

    for start, end in period_ranges:
        stats = weekly_stats(data, start, end, user_email)

        if date1.date() <= end and start <= date2.date():
            weekly_stats_list2.append((start, end, stats))
        else:
            weekly_stats_list1.append((start, end, stats))

    save_csv(output_csv1, weekly_stats_list1)
    save_csv(output_csv2, weekly_stats_list2)
