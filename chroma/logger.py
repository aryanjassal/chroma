from __future__ import annotations

from typing import Optional


class Term:
    RESET = "\033[0m"
    FG_MUTE = "\033[2m"
    FG_INFO = "\033[34m"
    FG_WARN = "\033[33m"
    FG_EROR = "\033[31m"


class LogLevel:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    QUIET = 4
    SILENT = 9


class Logger:
    __logger: Optional[Logger] = None

    def __init__(self, log_level):
        self.level = log_level

    def debug(self, message) -> None:
        if self.level <= LogLevel.DEBUG:
            Logger.__out(
                f"{Term.FG_MUTE} DBUG {Term.RESET}",
                f"{Term.FG_MUTE}{message}{Term.RESET}",
            )

    def info(self, message) -> None:
        if self.level <= LogLevel.INFO:
            Logger.__out(
                f"{Term.FG_INFO} INFO {Term.RESET}",
                f"{Term.FG_MUTE}{message}{Term.RESET}",
            )

    def warn(self, message) -> None:
        if self.level <= LogLevel.WARN:
            Logger.__out(
                f"{Term.FG_WARN} WARN {Term.RESET}",
                f"{message}{Term.RESET}",
            )

    def error(self, message) -> None:
        if self.level <= LogLevel.ERROR:
            Logger.__out(
                f"{Term.FG_EROR} EROR {Term.RESET}",
                f"{message}{Term.RESET}",
            )

    @staticmethod
    def set_logger(logger: Logger) -> None:
        Logger.__logger = logger

    @staticmethod
    def get_logger() -> Logger:
        if Logger.__logger is not None:
            return Logger.__logger
        Logger.__logger = Logger(0)
        Logger.__logger.warn("Attempt to get logger None!")
        Logger.__logger.warn("Setting default loger with level DEBUG")
        return Logger.__logger

    @staticmethod
    def __out(prefix: str, message: str) -> None:
        lines = message.split("\n")
        for line in lines:
            print(f"{prefix} {line}")
