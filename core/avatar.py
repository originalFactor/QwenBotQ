# Copyright (C) 2024 originalFactor
#
# This file is part of QwenBotQ.
#
# QwenBotQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QwenBotQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.

'Get avatar'


async def get_avatar_path(self) -> Optional[str]:
    'Get the avatar path of the user'
    if not isdir('cache'):
        mkdir('cache')
    base_dir = f'cache/{self.id}'
    if not isdir(base_dir):
        mkdir(base_dir)
    files = listdir(base_dir)
    return base_dir+'/'+files[0] if files else None


@property
async def avatar(self) -> bytes:
    'Get the avatar of the user'
    file = await self.get_avatar_path()
    if not file or not await still_valid(
            datetime.fromtimestamp(float(split(file)[1].split('.')[0]))):
        try:
            resp = await http_client.get(f"http://q1.qlogo.cn/g?b=qq&nk={self.id}&s=640")
            resp.raise_for_status()
            content = resp.content
            if file:
                remove(file)
            with open(f'cache/{self.id}/{int(datetime.now().timestamp())}.png', 'wb') as f:
                f.write(content)
            return content
        except HTTPError as e:
            logger.warning(
                'Avartar download failed, using the old one.'
                f' Exception: {e}'
            )
    if file:
        with open(file, 'rb') as f:
            return f.read()
    return b''
