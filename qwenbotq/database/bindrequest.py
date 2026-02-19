# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from typing import Annotated

from beanie import Document, Indexed


class BindRequest(Document):
    from_id: Annotated[str, Indexed(unique=True)]
    to_id: Annotated[str, Indexed()]
    requested_session: str
