import os

import pandas as pd

from preprocessing.symptom_dates import get_symptom_dates


class User:
    """Represents a participant in the COVID-19 Wearables dataset.

    See https://www.nature.com/articles/s41551-020-00640-6#MOESM3
    """

    def __init__(
        self,
        user_id: str,
        sampling_rule: str = "1H",
        aggregate: str = "mean",
        load_steps: bool = False,
        load_sleep: bool = False,
    ) -> None:
        """Load all data for a specific user.

        Parameters
        ----------
        user_id : str
            User ID
        sampling_rule : str, optional
            How to subsample time series data, by default "1H" which means that we group the time data by hour. For possible values see the 'rule' parameter at https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
        aggregate : str, optional
            How to aggregate the grouped time series data, by default "mean". The aggregation method has to be an attribute of pd.DataFrame
        load_steps : bool, optional
            Whether to load step data, by default False
        load_sleep : bool, optional
            Whether to load sleep data, by default False
        """
        self.id = user_id
        self.sampling_rule = sampling_rule
        self.aggregate = aggregate

        # load heartrate data
        raw_hr = load_user_hr(self.id)

        # resample and aggregate
        self.hr = raw_hr.resample(sampling_rule)
        self.hr = getattr(self.hr, self.aggregate)()

        if load_steps is True:
            # load step data
            raw_steps = load_user_steps(self.id)

            # resample and aggregate
            self.steps = raw_steps.resample(sampling_rule)
            self.steps = getattr(self.steps, self.aggregate)()

        if load_sleep is True:
            # sleep data is indexed differently (timesteps + duration)
            raise NotImplementedError

        # load label data (symptom + diagonsis dates for each COVID user)
        self.label_data = get_symptom_dates()


def load_user_hr(user_id: str) -> pd.DataFrame:
    hr_path = os.path.join(
        os.getcwd(), "data", "COVID-19-Wearables", f"{user_id}_hr.csv"
    )

    # don't catch exception here
    df = pd.read_csv(hr_path)

    # reshape df to have datetime as index
    hr = df.pivot(index="datetime", columns="user", values="heartrate")
    hr.index = pd.to_datetime(hr.index)

    return hr


def load_user_steps(user_id: str) -> pd.DataFrame:
    steps_path = os.path.join(
        os.getcwd(), "data", "COVID-19-Wearables", f"{user_id}_steps.csv"
    )

    # don't catch exception here
    df = pd.read_csv(steps_path)

    # reshape df to have datetime as index
    steps = df.pivot(index="datetime", columns="user", values="steps")
    steps.index = pd.to_datetime(steps.index)

    return steps


def load_user_sleep(user_id: str) -> pd.DataFrame:
    sleep_path = os.path.join(
        os.getcwd(), "data", "COVID-19-Wearables", f"{user_id}_sleep.csv"
    )

    # don't catch exception here
    sleep_df = pd.read_csv(sleep_path)

    return sleep_df
