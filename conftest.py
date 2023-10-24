import asyncio

import pytest

from examples.tasks import narq


@pytest.fixture(scope="session")
def loop():
    loop = asyncio.get_event_loop()
    return loop


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(loop, request):
    loop.run_until_complete(narq.init())
