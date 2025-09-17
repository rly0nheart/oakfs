import typing as t

from rich import print
from rich.panel import Panel

from . import __project__

__all__ = ["LogRoller"]


class LogRoller:
    def __init__(self, name: str = __project__):
        self.name = name

    def _log(self, msg_type: t.Literal["error", "warning", "info"], msg: str):
        """
        Internal logging method to display messages with styles.

        :param msg_type: Type of message (error, warning, info)
        :param msg: Message content
        """

        styles = {
            "error": "bold red",
            "warning": "bold yellow",
            "info": "#80B3FF",
        }
        panel = Panel(
            f"{self.name}: {msg}",
            highlight=True,
            border_style=styles.get(msg_type, "bold #FF10F0"),
        )
        print(panel)

    def info(self, msg: str):
        """
        Log an informational message.

        :param msg: Message content
        """

        self._log(msg_type="info", msg=msg)

    def warning(self, msg: str):
        """
        Log a warning message.

        :param msg: Message content
        """

        self._log(msg_type="warning", msg=msg)

    def error(self, msg: str):
        """
        Log an error message.

        :param msg: Message content
        """

        self._log(msg_type="error", msg=msg)
