import pytest

from tgintegration import Response

from .congtest import *

pytestmark = pytest.mark.asyncio


async def test_start(controller, client):
    async with controller.collect(count=1) as res:  # type: Response
        await client.send_message(controller.peer, '/start')

    assert res.num_messages == 1

    if 'Здесь ты' in res[0].text:
        pass
    else:
        assert 'Hello!' in res[0].text
        async with controller.collect(count=1) as res:  # type: Response
            await client.send_message(controller.peer, 'Нет')

        assert res.num_messages == 1
        assert 'Что тогда' in res[0].text

