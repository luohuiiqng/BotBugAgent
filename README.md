## BotBugAgent

BotBugAgent 是一个面向 GitHub Pull Request 的 **mini Bugbot** 原型项目。  
它通过接收 GitHub Webhook 事件，拉取 PR 的代码变更（diff），后续将集成大语言模型（LLM），对代码进行自动审查并在 PR 中给出有价值的评论建议。

当前阶段目标：

- 完成从 GitHub → Webhook 服务 → 拉取 PR diff 的基础链路；
- 逐步接入 LLM，对 PR 生成整体 Review 说明和评论；
- 后续按计划接入简单工具（如 linter / 测试结果）与评测流程（evals）。

---

### 软件架构

整体采用「GitHub App + Webhook 服务 + LLM Agent（规划中）」的架构。

- **GitHub 仓库 / GitHub App**
  - 仓库：`luohuiiqng/BotBugAgent`
  - GitHub App：
    - 订阅 Pull Request 相关事件；
    - 通过 Webhook 将事件推送到本地/服务器上的 BotBugAgent 服务。

- **Webhook / API 服务（Python + FastAPI）**
  - 位置：`app/main.py`
  - 职责：
    - 提供 `/webhook/github` 接口接收 GitHub Webhook；
    - 解析 `pull_request` 事件；
    - 使用 GitHub API 拉取 PR 的文件变更列表与 diff（patch）；
    - 将信息输出到日志（当前阶段），后续在此基础上调用 LLM 并回写评论。

- **LLM Agent 层（规划中）**
  - 使用 Python + LangChain / DeepAgents 等方式封装：
    - 接收 PR 的 diff 和元数据；
    - 调用 LLM 生成整体 Review、逐文件/逐片段建议；
    - 通过 GitHub API 在 PR 下创建评论；
    - 后续加入工具结果（linter / 测试）与评测框架。

当前项目结构（简化）：

```text
BotBugAgent/
  app/
    main.py                 # FastAPI 应用入口，接收 GitHub Webhook，拉取 PR diff
  docs/
    mini-bugbot-plan.md     # mini Bugbot 项目整体规划
  README.md                 # 项目说明（本文件）
  pyproject.toml            # Python 项目依赖与配置（若使用 uv/Poetry）
```

---

### 部署与运行（本地开发）

#### 1. 克隆项目并安装依赖

```bash
git clone https://github.com/luohuiiqng/BotBugAgent.git
cd BotBugAgent

# 使用 uv（示例）
uv sync
# 或：
# uv add fastapi uvicorn[standard] requests
```

#### 2. 启动 FastAPI 服务

```bash
uv run uvicorn app.main:app --reload --port 8000
```

访问：

```text
http://127.0.0.1:8000/health
```

预期返回：

```json
{"status": "ok"}
```

#### 3. 使用 ngrok 暴露本地端口

开发阶段，为了让 GitHub 能访问本地服务，可以使用 ngrok：

```bash
ngrok http 8000
```

记下 ngrok 分配的 URL，例如：

```text
https://xxxx-xx-xx-xx.ngrok-free.app
```

Webhook URL 将是：

```text
https://xxxx-xx-xx-xx.ngrok-free.app/webhook/github
```

#### 4. 创建 GitHub App 并配置 Webhook

1. GitHub → 头像 → `Settings` → `Developer settings` → `GitHub Apps` → `New GitHub App`。
2. 关键配置：
   - **GitHub App name**：如 `BotBugAgent-App`
   - **Homepage URL**：`https://github.com/luohuiiqng/BotBugAgent`
   - **Webhook URL**：`https://xxxx-xx-xx-xx.ngrok-free.app/webhook/github`
   - **Webhook secret**：任意字符串（后续可用于校验）
3. 权限与事件（最简）：
   - Repository permissions:
     - Pull requests：Read-only（后续加评论时改为 Read & write）
     - Contents：Read-only
   - Subscribe to events:
     - 勾选 **Pull requests**
4. 创建后，在 App 页面点击 **Install App**，安装到 `BotBugAgent` 仓库。

#### 5. 配置 GitHub Token（用于调用 GitHub API）

开发阶段可以使用 Personal Access Token：

```bash
# PowerShell 示例
$env:GITHUB_TOKEN = "your_token_here"
```

FastAPI 会从环境变量中读取 `GITHUB_TOKEN`，用于调用 GitHub API 拉取 PR 文件信息。

#### 6. 验证 Webhook 与 PR 事件

1. 确保：
   - `uvicorn` 服务在运行；
   - `ngrok http 8000` 在运行；
   - GitHub App 已安装到 `BotBugAgent` 仓库；
   - Webhook URL 指向最新 ngrok 地址。
2. 在 `BotBugAgent` 仓库：
   - 创建新分支并修改代码（如新增 `app/test` 文件或修改 `main.py`）；
   - 提交并 push 到新分支；
   - 在 GitHub 上以 `base: main`, `compare: 新分支` 创建 Pull Request。
3. 观察运行 `uvicorn` 的终端日志，预期可以看到：

```text
[Webhook] PR #1 opened: ... in luohuiiqng/BotBugAgent

=== File: app/main.py ===
@@ ...diff 片段...
```

这表示基础链路（Webhook + 拉取 diff）已经跑通。

---

### 后续规划

后续开发将按 `docs/mini-bugbot-plan.md` 中的规划继续推进：

- 接入 LLM，对 PR 生成整体 review 文本，并在 PR 中发布评论；
- 演进为逐文件/逐片段的结构化评论，控制评论数量与噪音；
- 集成简单 linter / 测试结果，辅助判断问题；
- 构建基础评测脚本，对不同策略和 Prompt 的效果进行量化比较；
- 打磨安装体验与文档，使其成为可供他人试用的 mini Bugbot Demo。
