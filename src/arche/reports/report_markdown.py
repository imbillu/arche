from functools import partial
from typing import Dict

from arche.reports import Report
from arche.rules.result import Level, Outcome, Result
from colorama import Fore, Style
from IPython.display import display_markdown
import pandas as pd

display_markdown = partial(display_markdown, raw=True)


class ReportMarkdown(Report):
    def __init__(self):
        self.results: Dict[str, Result] = {}

    def save(self, result: Result) -> None:
        self.results[result.name] = result

    @staticmethod
    def write_color_text(text: str, color: Fore = Fore.RED) -> None:
        print(color + text + Style.RESET_ALL)

    @staticmethod
    def write_rule_name(rule_name: str) -> None:
        display_markdown(f"{rule_name}:")

    @classmethod
    def write(cls, text: str) -> None:
        print(text)

    def write_summaries(self) -> None:
        for result in self.results.values():
            self.write_summary(result)

    @classmethod
    def write_summary(cls, result: Result) -> None:
        cls.write_rule_name(result.name)
        if not result.messages:
            cls.write_rule_outcome(Outcome.PASSED, Level.INFO)
        for level, rule_msgs in result.messages.items():
            for rule_msg in rule_msgs:
                cls.write_rule_outcome(rule_msg.summary, level)

    @classmethod
    def write_rule_outcome(cls, outcome: str, level: Level = Level.INFO) -> None:
        if isinstance(outcome, Outcome):
            outcome = outcome.name
        msg = f"\t{outcome}"
        if level == Level.ERROR:
            cls.write_color_text(msg)
        elif level == Level.WARNING:
            cls.write_color_text(msg, color=Fore.YELLOW)
        elif outcome == Outcome.PASSED.name:
            cls.write_color_text(msg, color=Fore.GREEN)
        else:
            cls.write(msg)

    def write_details(self, short: bool = False, keys_limit: int = 10) -> None:
        for result in self.results.values():
            if result.detailed_messages_count:
                display_markdown(
                    f"{result.name} ({result.detailed_messages_count} message(s)):"
                )
                self.write_rule_details(result, short, keys_limit)
            for f in result.figures:
                f.show()
            display_markdown("<br>")

    @classmethod
    def write_rule_details(
        cls, result: Result, short: bool = False, keys_limit: int = 10
    ) -> None:
        for rule_msgs in result.messages.values():
            for rule_msg in rule_msgs:
                if rule_msg.errors:
                    cls.write_detailed_errors(rule_msg.errors, short, keys_limit)
                elif rule_msg.detailed:
                    cls.write(rule_msg.detailed)

    @classmethod
    def write_detailed_errors(cls, errors: Dict, short: bool, keys_limit: int) -> None:
        error_messages = sorted(errors.items(), key=lambda i: len(i[1]), reverse=True)

        if short:
            keys_limit = 5
            error_messages = error_messages[:5]

        for attribute, keys in error_messages:
            if isinstance(keys, list):
                keys = pd.Series(keys)
            if isinstance(keys, set):
                keys = pd.Series(list(keys))

            sample = Report.sample_keys(keys, keys_limit)
            display_markdown(
                f"{len(keys)} items affected - {attribute}: {sample}", raw=True
            )

    def display(self, short: bool = False) -> None:
        self.report.write_summaries()
        self.report.write("\n" * 2)
        self.report.write_details(short)
