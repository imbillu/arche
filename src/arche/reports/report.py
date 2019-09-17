from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict
import numpy as np

from arche.rules.result import Result
from arche import SH_URL


class Report(ABC):
    """
    Base class for reports
    """

    def __init__(self):
        self.results: Dict[str, Result] = {}

    def save(self, result: Result) -> None:
        self.results[result.name] = result

    @abstractmethod
    def write_summaries(self) -> None:
        pass

    @abstractmethod
    def write_details(self, short: bool = False, keys_limit: int = 10) -> None:
        pass

    @abstractmethod
    def display(self, short: bool = False) -> None:
        pass

    @staticmethod
    def sample_keys(keys: pd.Series, limit: int) -> str:
        if len(keys) > limit:
            sample = keys.sample(limit)
        else:
            sample = keys

        def url(x: str) -> str:
            if SH_URL in x:
                return f"[{x.split('/')[-1]}]({x})"
            key, number = x.rsplit("/", 1)
            return f"[{number}]({SH_URL}/{key}/item/{number})"

        # make links only for Cloud data
        if keys.dtype == np.dtype("object") and "/" in keys.iloc[0]:
            sample = sample.apply(url)

        return ", ".join(sample.apply(str))
