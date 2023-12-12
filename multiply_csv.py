import csv
import sys

import consts

def change_values(filename, multiply_val : list[int]):

    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        modified_rows = []
        for row in reader:
            new_row = {}
            for i, (column, value) in enumerate(row.items()):
                new_value = float(value) * multiply_val[i]
                new_row[column] = new_value
            modified_rows.append(new_row)

    with open("modified_" + filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(modified_rows)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    multiply_val = [1.1, 0.1, 1.8, 1.1, 1, 1.5]
    change_values(sys.argv[1], multiply_val)
