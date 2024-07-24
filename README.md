# QwenQBot

A bot using NoneBot2 that supports chat with Aliyun Qwen LLM.

## How to start

Here are classic instructions to run this project over QQNT.

### Check Python version

```sh
python3 -V
```

Make sure your python3 version is higher than `3.8`.
Otherwise, you should install it, recommend [PyENV](https://github.com/pyenv/pyenv).

### Install requirements

```sh
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install nb-cli
python3 -m pip install dashscope
```

Other requirements should be installed automatically by `nb-cli`.
Otherwise, There are these requirments:
```
Drivers:
- httpx
- websockets

Adapters:
- Satori
```

### Setup server

You should have a QQNT application installed on your computer.
Otherwise, just download it [here](https://im.qq.com/index/#downloadAnchor)

Then you should install a LiteLoaderQQNT by the installer [here](https://github.com/Mzdyl/LiteLoaderQQNT_Install/)

Then open the application, open settings->LiteLoaderQQNT, then open the data directory.
(It usually be `C:\Users\YourUserName\Documents\LiteLoader` for Windows or `/opt/LiteLoader` for linux)

Download the `api`, `event` engine and `chronocat` itself [here](https://github.com/chrononeko/chronocat/releases),
`unzip` it to `{YOUR-DATA-DIRECTORY}/plugins`

Then restart your QQNT application.

Done.

### Change configuration

Unfortunely, the configuration isn't same for everyone.
That means you have to create one yourself.

Rename `.env.example` to `.env.prod`,
then open `~/.chronocat/config/chronocat.yml`,
so you can know what value should you set.

### Register dashscope

Simply register an account on Aliyun and charge, then create access api-key [here](https://dashscope.aliyun.com/).

Save the key to `QWEN_API_KEY` file.

### Run!

```sh
nb run
```

## Resources

- [NoneBot Document](https://nonebot.dev/)
- [Satori Nonebot Adapter GitHub](https://github.com/nonebot/adapter-satori?tab=readme-ov-file)
- [Chronocat Document](https://chronocat.vercel.app/)

## Community

Is that thing really exists? IDK.

If you want to report bugs, or something more, just [open an issue](https://github.com/originalFactor/QwenBotQ/issues)!