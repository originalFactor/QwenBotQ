# QQ 娱乐机器人

使用 Nonebot2 + NapCatQQ 驱动的娱乐型 QQ 机器人

## 功能特性

- **AI 对话**：接入 OpenAI 兼容 API，支持多模型、自定义提示词、工具调用与联网搜索（可选）。
- **长期记忆**：基于向量数据库（Qdrant）+ 嵌入/重排模型的 RAG 记忆，支持会话上下文持久化与自动总结（可选）。
- **识图搜图**：图片搜索功能，可选 ExHentai 源（需 Cookies）。
- **撤回图片缓存**：对监听会话中被撤回的图片自动保存，支持超级用户检索与打包下载。
- **E-Hentai 下载**：内置 `ehentaix` 库，支持图库搜索、缩略图与整本下载。
- **娱乐功能**：积分/签到系统、绑定账号、换老婆、抽奖等。
- **B站动态订阅**：订阅 UP 主动态并推送至指定群/用户（可选）。
- **超级用户管理**：私聊命令管理监听会话、撤回图、拉黑、续费等。

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

## 开发与维护

`AGENTS.md`（根目录与 `EHentaiX/` 各有一份）是面向 AI 助手的维护说明，包含项目结构、常用命令、架构边界与约定。开发者修改代码时，应与代码同步更新 `AGENTS.md` 与 `README.md`，确保描述与实际行为一致。

## ⚖️ License Migration Notice

**Important:** This project has officially transitioned its licensing from **GPLv3** to **MIT** effective **February 10, 2026**.

### Dual-License Breakdown

- **Legacy Code:** All versions, tags, and commits submitted **prior to February 10, 2026**, remain licensed under the [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html).
- **Current & Future Code:** All new versions, features, and commits submitted **on or after February 10, 2026**, are distributed under the [MIT License](https://mit-license.org/).

This transition is intended to provide maximum flexibility for our users and to encourage broader integration within the ecosystem.

## License

- [GPLv3 License](LICENSE-GPLv3) (Before 2026/2/11)
- [MIT License](LICENSE) (After 2026/2/11)
