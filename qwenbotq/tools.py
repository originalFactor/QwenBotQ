# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from ssl import PROTOCOL_TLS_CLIENT
from contextlib import asynccontextmanager
from truststore import SSLContext
from httpx import AsyncClient

def make_client(**kwargs) -> AsyncClient:
    return AsyncClient(verify=SSLContext(PROTOCOL_TLS_CLIENT), **kwargs)

@asynccontextmanager
async def client(**kwargs):
    async with make_client(**kwargs) as client:
        yield client
