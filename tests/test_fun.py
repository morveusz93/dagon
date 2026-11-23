from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from cogs import fun
from cogs.fun import Fun, _extension


@pytest.mark.parametrize(
    "url, ext",
    [
        ("https://x/a.GIF", ".gif"),
        ("https://x/a.jpg?size=1", ".jpg"),
        ("https://x/a.webp", ".webp"),
        ("https://x/noext", ".png"),
    ],
)
def test_extension(url, ext):
    assert _extension(url) == ext


class FakeResponse:
    def __init__(self, *, json=None, text="", body=b"img", status=200):
        self._json, self._text, self._body, self.status = json, text, body, status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(MagicMock(), (), status=self.status)

    async def json(self, content_type=None):
        return self._json

    async def text(self):
        return self._text

    async def read(self):
        return self._body


def make_cog(routes):
    session = MagicMock()
    session.get.side_effect = lambda url: routes[url]
    bot = MagicMock(http_session=session)
    return Fun(bot)


def make_ctx():
    ctx = MagicMock()
    ctx.send = AsyncMock()
    ctx.author.mention = "@tester"
    ctx.typing.return_value.__aenter__ = AsyncMock()
    ctx.typing.return_value.__aexit__ = AsyncMock(return_value=False)
    return ctx


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, api_url, payload, filename",
    [
        ("cat", fun.CATS_API_URL, [{"url": "https://img/c.jpg"}], "dagon.jpg"),
        ("dog", fun.DOGS_API_URL, [{"url": "https://img/d.gif"}], "dagon.gif"),
        ("duck", fun.DUCK_API_URL, {"url": "https://img/k.jpg"}, "dagon.jpg"),
        ("fox", fun.FOX_API_URL, {"image": "https://img/f.png"}, "dagon.png"),
    ],
)
async def test_animal_commands_send_picture(command, api_url, payload, filename):
    img_url = (
        payload[0]["url"] if isinstance(payload, list) else next(iter(payload.values()))
    )
    cog = make_cog({api_url: FakeResponse(json=payload), img_url: FakeResponse()})
    ctx = make_ctx()

    await getattr(cog, command).callback(cog, ctx)

    ctx.send.assert_awaited_once()
    assert "@tester" in ctx.send.call_args.args[0]
    assert ctx.send.call_args.kwargs["file"].filename == filename


@pytest.mark.asyncio
async def test_motivate_uses_text_response_as_image_url():
    cog = make_cog(
        {
            fun.MOTIVATE_API_URL: FakeResponse(text="https://img/m.jpg\n"),
            "https://img/m.jpg": FakeResponse(),
        }
    )
    ctx = make_ctx()

    await cog.motivate.callback(cog, ctx)

    assert ctx.send.call_args.kwargs["file"].filename == "dagon.jpg"


@pytest.mark.asyncio
async def test_api_error_is_reported_to_user():
    cog = make_cog({})
    ctx = make_ctx()
    error = MagicMock(original=aiohttp.ClientError("boom"))

    await cog.cog_command_error(ctx, error)

    ctx.send.assert_awaited_once_with(
        "Dagon nie zdołał dziś nic namalować. Spróbuj później."
    )
