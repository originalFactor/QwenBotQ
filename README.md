# QQ 娱乐机器人

使用 Nonebot2 + NapCatQQ 驱动的娱乐型 QQ 机器人

## 部署

### 环境要求

- Python 3.11
- MongoDB
- NapCatQQ / 其他 Onebot V11 协议驱动，设置正向 Websocket 连接
- Git
- OpenAI Format Api Key （若启用 AI 功能，如需记忆还需 Embedder 模型，若想要更好体验还需 Reranker 模型）
- Qdrant （若启用 AI 记忆功能）

### 安装步骤

1. 克隆项目仓库

```bash
git clone https://github.com/originalFactor/QwenBotQ.git
cd QwenBotQ
```

2. 安装依赖

```bash
pip install poetry
poetry install
```

3. 编辑配置文件

```bash
cp .env.example .env
vim .env  # 根据提示编辑
cp config.example.yml config.yml
vim config.yml  # 根据提示编辑
```

4. 运行Bot

```bash
poetry run python bot.py
```

## ⚖️ License Migration Notice

**Important:** This project has officially transitioned its licensing from **GPLv3** to **MIT** effective **February 10, 2026**.

### Dual-License Breakdown

- **Legacy Code:** All versions, tags, and commits submitted **prior to February 10, 2026**, remain licensed under the [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html).
- **Current & Future Code:** All new versions, features, and commits submitted **on or after February 10, 2026**, are distributed under the [MIT License](https://mit-license.org/).

This transition is intended to provide maximum flexibility for our users and to encourage broader integration within the ecosystem.

## License

- [GPLv3 License](LICENSE-GPLv3) (Before 2026/2/11)
- [MIT License](LICENSE) (After 2026/2/11)
