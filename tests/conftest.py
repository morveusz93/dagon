from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    ctx.author.mention = "@tester"
    ctx.typing.return_value.__aenter__ = AsyncMock()
    ctx.typing.return_value.__aexit__ = AsyncMock(return_value=False)
    return ctx
