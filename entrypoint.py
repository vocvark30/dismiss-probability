import main
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List
import time
import os
import csv

app = FastAPI()

class Parameters(BaseModel):
    input_csv: str
    user_emails: List[str]
    start_date1: datetime
    end_date1: datetime
    start_date2: datetime
    end_date2: datetime

def get_unique_values_from_csv(csv_path):
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        from_values = set()
        to_values = set()

        for row in reader:
            from_values.add(row['From'])
            to_values.add(row['To'])

    return from_values.union(to_values)


@app.post("/process_data")
async def process_data(params: Parameters):
    print(f"Received Parameters: {params}")

    tmp_filepath = f'{time.time_ns()}.csv'

    with open(tmp_filepath, 'w') as file:
        file.write(params.input_csv)

    users = set(params.user_emails)
    users_csv = get_unique_values_from_csv(tmp_filepath)

    if len(users.difference(users_csv)) != 0:
        os.remove(tmp_filepath)
        raise ValueError("Wrong user email input: there are no such users")

    res = main.users_probability(
        tmp_filepath,
        params.user_emails,
        params.start_date1,
        params.end_date1,
        params.start_date2,
        params.end_date2
    )

    os.remove(tmp_filepath)

    probabilities = [f'{val * 100:.1f}%' for val in res]
    response = [f'{name}: {p}' for name, p in zip(params.user_emails, probabilities)]

    return {"results":'<br>' + '<br>'.join(response)}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    with open("index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
