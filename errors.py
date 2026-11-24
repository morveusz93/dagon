from discord.ext import commands


class DagonError(commands.CommandError):
    """Błąd, którego treść można pokazać użytkownikowi."""


def unwrap(error: BaseException) -> BaseException:
    """Zdejmij opakowania discord.py (CommandInvokeError, HybridCommandError...)."""
    while getattr(error, "original", None) is not None:
        error = error.original
    return error
