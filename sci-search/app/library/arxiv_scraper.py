import os
import json
import arxiv
import argparse

from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from tqdm import tqdm

ARXIV_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
CLI_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_ROOT_DIRECTORY = "/Users/Viktor/git/playground/sci-search/arxiv-files"
DOCUMENT_DATE_NAME = "published"

def download_documents_from_dates_to_path(dates: List[datetime], path: str):
    docs = get_documents_from_dates(dates)
    download_documents(docs, path)

def get_documents_from_dates(dates: List[datetime]) -> List[dict]:
    interesting_dates = format_interesting_dates(dates)
    last_date = interesting_dates[-1]

    interesting_docs = []

    query = arxiv.query(query="cat:cs.CL", sort_by="submittedDate", sort_order="descending", iterative=True)
    for d in query():
        current_document_date = parse_arxiv_date(d[DOCUMENT_DATE_NAME])
        if current_document_date < last_date:
            break

        elif current_document_date in interesting_dates:
            interesting_docs.append(d)

    print(f'Found {len(interesting_docs)} documents in requested range!')
    return interesting_docs

def format_interesting_dates(dates: List[datetime]) -> List[datetime]:
    return sorted([set_default_time_units(d) for d in dates], reverse=True)

def parse_arxiv_date(date_string: str) -> datetime:
    date = datetime.strptime(date_string, ARXIV_DATE_FORMAT)
    return set_default_time_units(date)

def set_default_time_units(date: datetime) -> datetime:
    return date.replace(**{"hour": 0, "minute": 0, "second": 0, "microsecond": 0})

def download_documents(docs: List[dict], root_path: str):
    for d in tqdm(docs, desc = f"Downloading {len(docs)} documents to path {os.path.abspath(root_path)}"):
        arxiv.arxiv.download(d, get_storage_path(root_path, d), slugify=get_file_name)
        d["file_path"] = f"{get_storage_path(root_path, d)}/{get_file_name(d)}"

    with open(f"{root_path}/metadata.json", "a+") as metadata_file:
        for d in docs:
            metadata_file.write(json.dumps(d) + "\n")


def get_storage_path(root_path, doc: dict) -> str:
    date = parse_arxiv_date(doc[DOCUMENT_DATE_NAME])
    dir_path = f'{root_path}/{prettify_date(date)}/'
    if not os.path.isdir(dir_path):
        Path(dir_path).mkdir(parents=True)

    return dir_path

def get_file_name(doc: dict) -> str:
    return doc["id"].split("/")[-1]

def get_n_previous_days(n: int) -> List[datetime]:
    base = datetime.today()
    return [base - timedelta(days=x) for x in range(n)]

def get_dates_in_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    days_diff = abs((start_date - end_date).days) + 1
    return [max(start_date, end_date) - timedelta(days=d) for d in range(days_diff)]

def prettify_dates(dates: List[datetime]) -> str:
    return ", ".join([prettify_date(d) for d in dates])

def prettify_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


parser = argparse.ArgumentParser(description="Download arxiv files last n days")

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-n", "--n_days", metavar="days", type=int, help="Number of days in the past to fetch documents from.")
group.add_argument("-d", "--date", metavar="date", type=str, help="Date to extract documents from. Has to be on format 'Y-M-D'")
group.add_argument("-r", "--range", metavar=("date_start", "date_end"), type=str, nargs=2, help=f"Range of days to extract documents from. Has to be on format '{CLI_DATE_FORMAT}'")

parser.add_argument("-p", "--path", metavar="path", type=str, help="Root path to store exported files in", default=DEFAULT_ROOT_DIRECTORY)

args = parser.parse_args()
if args.n_days:
    date_range = get_n_previous_days(args.n_days)
elif args.range:
    start = datetime.strptime(args.range[0], CLI_DATE_FORMAT)
    end = datetime.strptime(args.range[1], CLI_DATE_FORMAT)
    date_range = get_dates_in_range(start, end)
elif args.date:
    date_range = [datetime.strptime(args.date, CLI_DATE_FORMAT)]

if len(date_range) == 1:
    print(f"Extracting documents from date {prettify_dates(date_range)}")
else:
    print(f"Extracting documents from date range {prettify_dates(date_range)}...")

download_documents_from_dates_to_path(date_range, args.path)
