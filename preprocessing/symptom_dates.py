import os
from datetime import datetime
from typing import List, Union

import pandas as pd


def get_symptom_dates() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(os.getcwd(), "data", "covid_symptom_dates_raw.csv"))

    # lowercase columns
    df.columns = [col.lower() for col in df.columns]

    # filter non-covid
    df = df.query("category == 'COVID-19'")

    # drop any rows with NaN values
    df = df.dropna(how="any")

    # map timestamps to datetime objects
    df["symptom_dates"] = map_timestamps_to_dates(df["symptom_dates"].tolist())
    df["covid_diagnosis_dates"] = map_timestamps_to_dates(
        df["covid_diagnosis_dates"].tolist()
    )
    df["recovery_dates"] = map_timestamps_to_dates(df["recovery_dates"].tolist())

    return df


def timestamp_to_date(stamp: str) -> datetime:
    # Timestamp('2028-01-16 00:00:00') => datetime object
    return datetime.strptime(stamp.lstrip()[11:-2], "%Y-%m-%d %H:%M:%S")


def map_timestamps_to_dates(stamps: List[str]) -> List[Union[datetime, List[datetime]]]:
    # remove NaT (done with dropna and replacing [NaT] with NaN)
    # stamps = list(filter(lambda stamp: stamp != "[NaT]", stamps))

    # cast strings to lists
    stamps = [stamp.split("[")[1].split("]")[0].split(",") for stamp in stamps]

    # cast list of strings to list of datetimes
    dates = [list(map(timestamp_to_date, stamp)) for stamp in stamps]

    return dates
