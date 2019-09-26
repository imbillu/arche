from typing import Dict

from arche import SH_URL
from arche.rules.result import Level, Result

from arche.rules.result import Level, Outcome, Result
import numpy as np

import pandas as pd

from jinja2 import Environment, FileSystemLoader, select_autoescape
from bleach import linkify

from IPython.display import HTML, display


class Report:
    def __init__(self):
        self.results: Dict[str, Result] = {}

        self.env = Environment(
            loader=FileSystemLoader('arche/templates/'),
            autoescape=select_autoescape(['html']),
        )
        self.env.filters['linkify'] = linkify
        self.env.filters['pd'] = pd

    def save(self, result: Result) -> None:
        self.results[result.name] = result

    def _rule_outcome(self, rule) -> str:
        """
        Returns the outcome status of a given rule
        """
        if not rule.messages:
            return "Passed"
        message_level = rule.messages.keys()
        if any([level.value == Level.ERROR.value for level in message_level]):
            return "Failed"
        elif any([level.value == Level.WARNING.value for level in message_level]):
            return "Warning"
        else:
            return "Skipped"

    def _order_rules(self, rules):
        """
        Returns an ordered list of Results
        """
        RULE_ORDER = ["Passed", "Failed", "Warning", "Skipped"]
        rules = sorted([(RULE_ORDER.index(self._rule_outcome(rule)), rule) for rule in rules],
                       key=lambda x: x[0]
                       )
        return [rule[1] for rule in rules]

    def display(self) -> None:
        for f in self.results.values():
            f.figures

        template = self.env.get_template('template.html')
        resultHTML = template.render(
            rules=list(self._order_rules(self.results.values())),
            rule_outcome=self._rule_outcome,
            pd=pd,
        )
        display(HTML(resultHTML), metadata={"isolated": True})

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
