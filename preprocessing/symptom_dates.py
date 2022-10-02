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

    # rename to be consistent with User class
    df.rename(columns={"participantid": "user"}, inplace=True)

    # set user_id as index
    df.set_index("user", inplace=True)

    # remove recovery dates and category (is always COVID)
    df = df.drop(["recovery_dates", "category"], axis=1)

    # remove multiple symptom and diagnosis dates
    df = filter_symptom_dates(df)

    return df


def filter_symptom_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce entires with multiple symptom and diagnosis dates to a single one.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe

    Returns
    -------
    pd.DataFrame
        Dataframe with a single diagnosis and symptom dates for each participant
    """

    # take min diagonsis date
    df["covid_diagnosis_dates"] = df["covid_diagnosis_dates"].apply(
        lambda dates: min(dates)
    )

    # find max symptom date <= min diagnosis date for every row
    def select_symptom_date(symptom_dates, diagnosis_date):
        dates = list(filter(lambda date: date <= diagnosis_date, symptom_dates))
        return max(dates)

    # take max symptom date from list smaller than diagnosis date
    df["symptom_dates"] = df.apply(
        lambda x: select_symptom_date(x["symptom_dates"], x["covid_diagnosis_dates"]),
        axis=1,
    )

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
