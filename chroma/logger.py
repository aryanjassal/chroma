from __future__ import annotations

from typing import Never


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


class Logger:
    __logger: Logger = None

    def __init__(self, log_level):
        self.level = log_level

    def debug(self, message):
        if self.level <= LogLevel.DEBUG:
            Logger.out(
                f"{Term.FG_MUTE} DBUG {Term.RESET}",
                f"{Term.FG_MUTE}{message}{Term.RESET}",
            )

    def info(self, message):
        if self.level <= LogLevel.INFO:
            Logger.out(
                f"{Term.FG_INFO} INFO {Term.RESET}",
                f"{Term.FG_MUTE}{message}{Term.RESET}",
            )

    def warn(self, message):
        if self.level <= LogLevel.WARN:
            Logger.out(
                f"{Term.FG_WARN} WARN {Term.RESET}",
                f"{message}{Term.RESET}",
            )

    def error(self, message):
        if self.level <= LogLevel.ERROR:
            Logger.out(
                f"{Term.FG_EROR} EROR {Term.RESET}",
                f"{message}{Term.RESET}",
            )

    def fatal(self, message, code=1) -> Never:
        Logger.out(
            f"{Term.FG_EROR} EROR {Term.RESET}",
            f"{message}{Term.RESET}",
        )
        exit(code)

    @staticmethod
    def set_logger(logger: Logger):
        Logger.__logger = logger

    @staticmethod
    def get_logger() -> Logger:
        return Logger.__logger

    @staticmethod
    def out(prefix: str, message: str) -> None:
        lines = message.split("\n")
        for line in lines:
            print(f"{prefix} {line}")
