# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from pydantic import BaseModel


class ImageSearchConfig(BaseModel):
    """The config class of image search."""

    exhentai_cookies: str | None = None
    file_server_port: int = 9080
    remote_host: str = "host.docker.internal"
    remote_port: int | None = None
