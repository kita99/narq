import asyncio

import pytest

from rearq import ReArq


@pytest.fixture(scope="session")
def loop():
    loop = asyncio.get_event_loop()
    return loop


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(loop, request):
    loop.run_until_complete(ReArq.init())

    request.addfinalizer(lambda: ReArq.close())