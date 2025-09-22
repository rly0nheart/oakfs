import typing as t

from rich.console import Console
from rich.panel import Panel

from . import __project__

__all__ = ["LogRoller", "console"]

console = Console()


class LogRoller:
    def __init__(self, name: str = __project__):
        self.name = name

    def _log(
        self,
        _type: t.Literal["error", "warning", "info", "summary"],
        text: str,
    ):
        """
        Internal logging method to display messages with styles.

        :param _type: Type of message (error, warning, info)
        :param text: Message content
        """

        styles = {
            "error": "bold red",
            "warning": "bold yellow",
            "summary": "#80B3FF",
            "info": "bold green",
        }
        panel = Panel(
            f"{self.name}: {text}",
            title=_type,
            title_align="left",
            highlight=True,
            border_style=styles.get(_type, "bold #FF10F0"),
        )
        console.print(panel)

    def info(self, text: str):
        """
        Log an informational message.

        :param text: Message content
        """

        self._log(_type="info", text=text)

    def warning(self, text: str):
        """
        Log a warning message.

        :param text: Message content
        """

        self._log(_type="warning", text=text)

    def error(self, text: str):
        """
        Log an error message.

        :param text: Message content
        """

        self._log(_type="error", text=text)

    def summary(self, text: str):
        """
        Log a summary message.

        :param text: Message content
        """

        self._log(_type="summary", text=text)
