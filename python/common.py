import logging
import pandas as pd
from pathlib import Path

LIST_ATTRS = ['genres', 'categories', 'steamspy_tags', 'platforms', 'developer', 'publisher']


def read_data(path: str):
    dp = Path(path)
    if not dp.exists():
        raise ValueError(f'ERROR: file "{dp}" does not exist')

    if not dp.is_file():
        raise ValueError(f'ERROR: "{dp}" is not a file')

    if dp.suffix != '.csv':
        raise ValueError(f'ERROR: file "{dp}" is not a CSV file (but should be)')

    return pd.read_csv(path)


def make_lists(df: pd.DataFrame):
    df['platforms'] = df['platforms'].str.split(';')
    df['categories'] = df['categories'].str.split(';')
    df['genres'] = df['genres'].str.split(';')
    df['steamspy_tags'] = df['steamspy_tags'].str.split(';')
    df['developer'] = df['developer'].str.split(';')
    df['publisher'] = df['publisher'].str.split(';')
    df['owners'] = df['owners'].str.split('-')
    return df


def configure_logger(loglevel_name: str):
    loglevel = logging._nameToLevel[loglevel_name] if loglevel_name in logging._nameToLevel else logging.ERROR
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        level=loglevel
    )
