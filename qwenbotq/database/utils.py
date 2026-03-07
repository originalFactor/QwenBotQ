# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from typing import NoReturn


def noid() -> NoReturn:
    raise RuntimeError("必须提供ID")
