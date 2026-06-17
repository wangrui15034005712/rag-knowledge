# OpenCode 常用命令速查手册

> **OpenCode** = 开源 AI 编程助手（由 SST/anomalyco 团队开发），终端优先，支持 **TUI 交互模式 + CLI 非交互模式 + 服务器模式**。  
> 官网：https://opencode.ai ｜ GitHub：https://github.com/sst/opencode  
> 安装确认：`opencode --version`

---

## 一、安装

| 方式 | 命令 |
|------|------|
| **一键脚本（推荐）** | `curl -fsSL https://opencode.ai/install \| bash` |
| **npm（全局）** | `npm i -g opencode-ai@latest` |
| **bun** | `bun add -g opencode-ai` |
| **Homebrew** | `brew install anomalyco/tap/opencode` |
| **Scoop（Windows）** | `scoop install opencode` |
| **Chocolatey（Windows）** | `choco install opencode` |
| **mise（跨平台）** | `mise use -g opencode` |
| **Arch Linux（AUR）** | `paru -S opencode-bin` |

> 升级：`opencode upgrade` 或 `opencode upgrade v0.1.48`  
> 卸载：`opencode uninstall`（加 `--keep-config` / `--keep-data` 可保留配置和数据）

---

## 二、核心命令速查

### 2.1 启动（默认 TUI 交互模式）

| 命令 | 说明 |
|------|------|
| `opencode` | 在当前目录启动 **TUI（终端图形界面）** |
| `opencode /path/to/project` | 指定项目路径启动 TUI |
| `opencode --model anthropic/claude-sonnet-4-20250514` | 启动时指定模型 |
| `opencode --agent <agent名>` | 启动时指定 Agent |
| `opencode --continue` / `-c` | 继续上次会话 |
| `opencode --session <ID>` / `-s` | 打开指定会话 |
| `opencode --prompt "提示语"` | 带初始提示启动 |

---

### 2.2 `opencode run` —— 非交互模式（脚本/自动化神器）

> 不打开 TUI，直接给提示拿结果。最适合：**CI/CD、批处理、快速查询**。

| 命令 | 说明 |
|------|------|
| `opencode run "解释这段代码"` | 最基本用法 |
| `opencode run -m anthropic/claude-sonnet-4-5 "Review this code"` | 指定模型 |
| `opencode run -c "继续上一个话题"` | 继续上次会话 |
| `opencode run -f src/main.ts -f package.json "分析这个项目"` | **附加文件**（可多个） |
| `opencode run --format json "列出所有 TS 文件"` | 输出原始 JSON（适合脚本解析） |
| `opencode run --share "生成项目文档"` | 自动分享会话 |
| `opencode run --title "Bug Fix" "修复登录问题"` | 设置会话标题 |
| `opencode run --attach http://localhost:4096 "解释 async/await"` | 挂到已运行的 server（避免 MCP 冷启动） |
| `echo "统计代码行数" \| opencode run "分析"` | 从 stdin 传入 |

**典型脚本用法：**

```bash
#!/usr/bin/env bash
# code-review.sh
opencode run --format json \
  -f src/UserService.java \
  -f src/repository/UserRepository.java \
  "Review these files for security issues and suggest fixes" \
  > review.json
```

---

### 2.3 `opencode serve` —— 无头服务器（API 模式）

| 命令 | 说明 |
|------|------|
| `opencode serve` | 启动 HTTP API 服务器（默认端口 **4096**） |
| `opencode serve --port 5000 --hostname 0.0.0.0` | 指定端口 + 允许远程 |
| `OPENCODE_SERVER_PASSWORD=密码 opencode serve` | 启用 HTTP Basic Auth |
| `opencode serve --cors http://localhost:5173` | 允许 CORS（可多次传） |

> 服务器 OpenAPI 文档：`http://localhost:4096/doc`  
> 然后另一边用 `opencode run --attach http://localhost:4096 "..."` 挂上去跑（免冷启动）

---

### 2.4 `opencode web` —— 带 Web 界面的服务器

| 命令 | 说明 |
|------|------|
| `opencode web` | 启动 HTTP 服务器 + 自动打开浏览器 |
| `opencode web --port 4096` | 指定端口 |
| `OPENCODE_SERVER_PASSWORD=密码 opencode web` | 启用认证 |

---

### 2.5 `opencode attach` —— 连接远程 OpenCode

```bash
# 终端 A：启动后端
opencode web --port 4096 --hostname 0.0.0.0

# 终端 B：把 TUI 挂上去
opencode attach http://10.20.30.40:4096
```

| 标志 | 简写 | 说明 |
|------|------|------|
| `--dir <路径>` | | TUI 工作目录 |
| `--continue` | `-c` | 继续上次会话 |
| `--session` | `-s` | 指定会话 ID |
| `--username` | `-u` | Basic Auth 用户名（默认 `opencode`） |
| `--password` | `-p` | Basic Auth 密码 |

---

## 三、认证与模型管理

### 3.1 认证 `opencode auth`

| 命令 | 说明 |
|------|------|
| `opencode auth login` | **交互式**选择提供商并配置 API Key（存入 `~/.local/share/opencode/auth.json`） |
| `opencode auth list` / `ls` | 列出已认证的提供商 |
| `opencode auth logout` | 清除某个提供商的凭据 |
| `opencode auth logout --all` | 清除全部 |

> OpenCode 也读环境变量和项目 `.env` 里的 Key，优先级：凭据文件 → env → `.env`

### 3.2 模型 `opencode models`

| 命令 | 说明 |
|------|------|
| `opencode models` | 列出所有可用模型（`provider/model` 格式） |
| `opencode models anthropic` | 只看某个提供商 |
| `opencode models --refresh` | 从 models.dev 刷新缓存 |
| `opencode models --verbose` | 显示详细信息（含费用元数据） |

---

## 四、Agent（智能体）管理

| 命令 | 说明 |
|------|------|
| `opencode agent list` | 列出所有可用 Agent |
| `opencode agent create` | **交互式引导**创建自定义 Agent（系统提示词 + 工具配置） |

---

## 五、MCP（Model Context Protocol）服务器管理

| 命令 | 说明 |
|------|------|
| `opencode mcp add` | 交互式添加本地/远程 MCP 服务器 |
| `opencode mcp list` / `ls` | 列出已配置 MCP 及连接状态 |
| `opencode mcp auth [名称]` | OAuth 认证到 MCP 服务器 |
| `opencode mcp auth ls` | 列出 OAuth 认证状态 |
| `opencode mcp logout [名称]` | 移除 OAuth 凭据 |
| `opencode mcp debug <名称>` | 调试 MCP 连接问题 |

---

## 六、会话（Session）管理

| 命令 | 说明 |
|------|------|
| `opencode session list` | 列出所有会话 |
| `opencode session list -n 10` | 最近 10 个会话 |
| `opencode session list --format json` | JSON 格式输出 |
| `opencode export [sessionID]` | 导出会话为 JSON（不传 ID 则交互选择） |
| `opencode import session.json` | 从本地文件导入 |
| `opencode import https://opncd.ai/s/abc123` | 从分享链接导入 |

---

## 七、统计

| 命令 | 说明 |
|------|------|
| `opencode stats` | 总体用量和成本 |
| `opencode stats --days 7` | 最近 7 天 |
| `opencode stats --tools 10` | 显示前 10 个工具调用 |
| `opencode stats --models 5` | 显示模型用量 Top 5 |
| `opencode stats --project ""` | 只看当前项目 |

---

## 八、GitHub / PR 集成

| 命令 | 说明 |
|------|------|
| `opencode github install` | 在仓库安装 GitHub Agent（配 Actions 工作流） |
| `opencode github run` | 运行 GitHub Agent（一般给 Actions 用） |
| `opencode pr 42` | 检出 PR #42 并启动 OpenCode 进入上下文 |
| `opencode pr 123 --model anthropic/claude-3.5-sonnet` | 指定模型审查 PR |

---

## 九、其他命令

| 命令 | 说明 |
|------|------|
| `opencode init` | 创建/更新 `AGENTS.md`（让 AI 理解项目结构） |
| `opencode acp "提交信息"` | 一键 `add + commit + push`（ACP 协议） |
| `opencode plugin` / `plug` | 安装插件 |
| `opencode upgrade` | 升级到最新版 |
| `opencode upgrade v0.1.48` | 升级到指定版本 |
| `opencode uninstall` | 卸载 |
| `opencode db path` | 打印数据库路径 |
| `opencode db [query]` | 数据库工具 |
| `opencode debug [command]` | 调试排障 |

---

## 十、全局标志（任何命令都能跟）

| 标志 | 简写 | 说明 |
|------|------|------|
| `--help` | `-h` | 显示帮助 |
| `--version` | `-v` | 打印版本 |
| `--print-logs` | | 把日志打到 stderr |
| `--log-level LEVEL` | | `DEBUG / INFO / WARN / ERROR` |
| `--pure` | | 禁用外部插件运行 |

---

## 十一、常用环境变量

| 变量 | 作用 |
|------|------|
| `OPENCODE_SERVER_PASSWORD` | serve/web 的 Basic Auth 密码（用户名默认 `opencode`） |
| `OPENCODE_SERVER_USERNAME` | 覆盖 Basic Auth 用户名 |
| `OPENCODE_CONFIG` | 指定配置文件路径 |
| `OPENCODE_CONFIG_DIR` | 指定配置目录 |
| `OPENCODE_DISABLE_AUTOUPDATE` | 禁用自动更新检查 |
| `OPENCODE_DISABLE_LSP_DOWNLOAD` | 禁用自动下载 LSP Server |
| `OPENCODE_DISABLE_AUTOCOMPACT` | 禁用自动上下文压缩 |
| `EDITOR` | `/editor` 和 `/export` 用的外部编辑器（`code`、`vim`、`nano` 等） |

---

## 十二、TUI 内部斜杠命令（在 OpenCode 交互界面里敲 `/`）

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助对话框 |
| `/new` / `/clear` | 新建会话 |
| `/sessions` / `/resume` / `/continue` | 列出/恢复会话 |
| `/export` | 导出当前会话为 Markdown（用 `$EDITOR` 打开） |
| `/compact` / `/summarize` | 压缩上下文 |
| `/models` | 列出可用模型 |
| `/themes` | 切换主题 |
| `/init` | 创建/更新 `AGENTS.md` |
| `/undo` | 撤销上一条消息 |
| `/redo` | 重做 |
| `/details` | 开关工具执行详情显示 |
| `/editor` | 用外部编辑器撰写消息 |
| `/share` / `/unshare` | 分享/取消分享会话 |
| `/quit` / `/q` | 退出 |

---

## 十三、实战小抄（Java 全栈常用场景）

### 快速代码审查
```bash
opencode run -f src/main/java/com/xxx/OrderService.java \
  "Review this file for concurrency bugs, null safety, and resource leaks"
```

### 生成文档注释 / JavaDoc 风格
```bash
opencode run -f src/service/PaymentService.java \
  "Add proper JavaDoc to all public methods, keep implementation unchanged"
```

### 分析 Maven/Gradle 依赖问题
```bash
opencode run -f pom.xml -f dependency-tree.txt \
  "Why is commons-collections3 still here? Find conflict and suggest exclusions"
```

### 启动 TUI 开始自由对话
```bash
cd /your/project
opencode
```

### 后台跑 server，另一个终端 attach（避免每次冷启动 MCP）
```bash
# 终端1
opencode serve --port 4096

# 终端2（日常用这个跑单次任务，热）
opencode run --attach http://localhost:4096 "解释 GatewayFilter 的执行链顺序"
```

---

> **提示**：`opencode --help` 和 `opencode <子命令> --help` 随时查。项目配置主要在 `~/.config/opencode/opencode.json`（或 `.opencode/` 项目级），`AGENTS.md` 是给 AI 读的"项目说明书"，值得认真维护。