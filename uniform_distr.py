import csv
from datetime import datetime, timedelta

def redistribute_dates(input_csv: str, output_csv: str, start_date: str, end_date: str):
    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    if start_date >= end_date:
        raise ValueError("Start date should be less than end date")

    # Read the input CSV
    rows = []
    with open(input_csv) as csvfile:
        csv_reader = csv.reader(csvfile, quotechar='"')
        for row in csv_reader:
            rows.append(row)

    num_emails = len(rows) - 1  # Exclude header row
    date_increment = (end_date - start_date) / num_emails

    # Replace the dates and write to the output CSV
    with open(output_csv, "w", newline='') as csvfile:
        csv_writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)

        # Write the header row
        csv_writer.writerow(rows[0])

        for i, row in enumerate(rows[1:], start=1):
            new_date = start_date + (date_increment * (i - 1))
            row[2] = new_date.strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow(row)


# Example usage
redistribute_dates("example.csv", "output.csv", "2022-10-01 12:00:00", "2022-12-22 12:00:00")
