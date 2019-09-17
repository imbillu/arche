from .report import Report
from typing import Dict

import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
from bleach import linkify
from arche.rules.result import Level, Result
from IPython.display import HTML, display


class ReportHtml(Report):
    def __init__(self):
        self.results: Dict[str, Result] = {}
        self.env = Environment(
            loader=PackageLoader('arche', 'reports'),
            autoescape=select_autoescape(['html']),
        )
        self.env.filters['linkify'] = linkify
        self.env.filters['pd'] = pd

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

    def write_summaries(self):

        template = self.env.get_template('template.html')
        resultHTML = template.render(
            rules=list(self._order_rules(self.results.values())),
            rule_outcome=self._rule_outcome,
            pd=pd,
        )
        display(HTML(resultHTML), metadata={"isolated": True})

    @classmethod
    def write_details(cls, short: bool = False, keys_limit: int = 10) -> None:
        pass

    def display(self, short: bool = False) -> None:
        self.write_summaries()
