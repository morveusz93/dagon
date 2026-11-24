import asyncio
from unittest.mock import MagicMock

import aiohttp
import pytest

from cogs import fun
from cogs.fun import Fun, _extension
from errors import DagonError


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
    def __init__(self, *, json=None, text="", body=b"img", status=200, exc=None):
        self._json, self._text, self._body = json, text, body
        self.status, self._exc = status, exc

    async def __aenter__(self):
        if self._exc:
            raise self._exc
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
    return Fun(MagicMock(http_session=session))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, api_url, payload, img_url, filename",
    [
        (
            "cat",
            fun.CATS_API_URL,
            [{"url": "https://i/c.jpg"}],
            "https://i/c.jpg",
            "dagon.jpg",
        ),
        (
            "dog",
            fun.DOGS_API_URL,
            [{"url": "https://i/d.gif"}],
            "https://i/d.gif",
            "dagon.gif",
        ),
        (
            "duck",
            fun.DUCK_API_URL,
            {"url": "https://i/k.jpg"},
            "https://i/k.jpg",
            "dagon.jpg",
        ),
        (
            "fox",
            fun.FOX_API_URL,
            {"image": "https://i/f.png"},
            "https://i/f.png",
            "dagon.png",
        ),
    ],
)
async def test_picture_commands_send_embed_with_image(
    ctx, command, api_url, payload, img_url, filename
):
    cog = make_cog({api_url: FakeResponse(json=payload), img_url: FakeResponse()})

    await getattr(cog, command).callback(cog, ctx)

    kwargs = ctx.send.call_args.kwargs
    assert kwargs["file"].filename == filename
    assert kwargs["embed"].image.url == f"attachment://{filename}"
    assert "@tester" in kwargs["embed"].description


@pytest.mark.asyncio
async def test_motivate_uses_text_response_as_image_url(ctx):
    cog = make_cog(
        {
            fun.MOTIVATE_API_URL: FakeResponse(text="https://i/m.jpg\n"),
            "https://i/m.jpg": FakeResponse(),
        }
    )

    await cog.motivate.callback(cog, ctx)

    assert ctx.send.call_args.kwargs["file"].filename == "dagon.jpg"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        FakeResponse(status=503),
        FakeResponse(json={}),  # brak klucza
        FakeResponse(exc=asyncio.TimeoutError()),
    ],
)
async def test_api_failure_raises_user_facing_error(ctx, response):
    cog = make_cog({fun.FOX_API_URL: response})

    with pytest.raises(DagonError):
        await cog.fox.callback(cog, ctx)
    ctx.send.assert_not_awaited()
