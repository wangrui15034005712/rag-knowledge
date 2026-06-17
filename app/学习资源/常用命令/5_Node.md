# Node.js 常用命令速查手册

> 适用版本：Node.js 18+ / 20+ LTS，npm 9+ / 10+。

---

## 一、Node.js 环境

| 命令 | 说明 |
|------|------|
| `node -v` | 查看 Node.js 版本 |
| `node -e "代码"` | 直接执行一行 JavaScript 代码 |
| `node -p "表达式"` | 执行并打印结果（等同于 `-e` + `console.log`） |
| `node -i` | 进入交互式 REPL 模式 |
| `node --check <文件.js>` | 检查语法但不执行 |
| `node --experimental-modules` | 启用实验性 ES Modules |
| `node --inspect` | 启动 Inspector（Chrome DevTools 调试） |
| `node --inspect-brk` | 启动 Inspector 并在第一行暂停 |
| `node --trace-warnings` | 显示警告的完整堆栈 |
| `node --max-old-space-size=4096` | 设置内存上限（单位 MB） |
| `node --require <模块>` | 预加载模块（如 `dotenv/config`） |
| `node --env-file=.env` | 从文件加载环境变量（Node 21.7+） |
| `node --watch <文件.js>` | 监听文件变化自动重启（Node 18+） |
| `node --title "标题"` | 设置进程标题 |
| `node --prof` | 启动 V8 性能分析 |
| `node --prof-process <isolate-*.log>` | 处理性能分析日志 |
| `node --heap-prof` | 启动堆快照分析 |
| `node --cpu-prof` | 启动 CPU 分析 |
| `node --experimental-strip-types` | 直接运行 TypeScript（Node 22.6+） |

---

## 二、npm 包管理

### 2.1 基础操作

| 命令 | 说明 |
|------|------|
| `npm -v` | 查看 npm 版本 |
| `npm init` | 交互式创建 package.json |
| `npm init -y` | 快速创建 package.json（默认值） |
| `npm install <包名>` | 安装包并写入 dependencies |
| `npm i <包名>` | 同上（简写） |
| `npm install <包名> --save-dev` | 安装为开发依赖（devDependencies） |
| `npm install <包名> -g` | 全局安装 |
| `npm install <包名>@版本` | 安装指定版本 |
| `npm install` | 根据 package.json 安装所有依赖 |
| `npm ci` | 根据 package-lock.json 精确安装（CI 环境推荐） |
| `npm uninstall <包名>` | 卸载包 |
| `npm update <包名>` | 更新包 |
| `npm outdated` | 查看可更新的包 |
| `npm list` | 列出当前项目的依赖树 |
| `npm list -g --depth=0` | 列出全局安装的顶层包 |
| `npm ls` | 同 list |
| `npm dedupe` | 减少依赖重复 |

### 2.2 发布与版本

| 命令 | 说明 |
|------|------|
| `npm login` | 登录 npm 账户 |
| `npm whoami` | 查看当前登录用户 |
| `npm publish` | 发布包 |
| `npm unpublish <包名>@版本` | 撤销发布（72小时内） |
| `npm deprecate <包名> "提示信息"` | 标记包为废弃 |
| `npm version patch` | 升级补丁版本（1.0.0 → 1.0.1） |
| `npm version minor` | 升级次要版本（1.0.0 → 1.1.0） |
| `npm version major` | 升级主要版本（1.0.0 → 2.0.0） |
| `npm version prerelease` | 升级预发布版本（1.0.0 → 1.0.1-0） |
| `npm pack` | 打包为 .tgz 文件 |

### 2.3 缓存与配置

| 命令 | 说明 |
|------|------|
| `npm cache ls` | 列出缓存内容 |
| `npm cache clean --force` | 清空缓存 |
| `npm config list` | 查看配置 |
| `npm config set <键> <值>` | 设置配置 |
| `npm config get <键>` | 获取配置 |
| `npm config delete <键>` | 删除配置 |
| `npm config set registry https://registry.npmmirror.com` | 设置镜像源 |
| `npm get registry` | 查看当前镜像源 |

### 常用镜像源

```
官方: https://registry.npmjs.org/
淘宝: https://registry.npmmirror.com/
腾讯: https://mirrors.cloud.tencent.com/npm/
华为: https://repo.huaweicloud.com/repository/npm/
```

### 2.4 审计与安全

| 命令 | 说明 |
|------|------|
| `npm audit` | 检查依赖安全漏洞 |
| `npm audit fix` | 自动修复可修复的漏洞 |
| `npm audit fix --force` | 强制修复（可能破坏兼容性） |
| `npm fund` | 查看依赖的资助信息 |

---

## 三、npx（包执行器）

| 命令 | 说明 |
|------|------|
| `npx <包名>` | 执行包（无需全局安装） |
| `npx <包名>@版本` | 执行指定版本的包 |
| `npx --yes <包名>` | 自动同意安装 |
| `npx --no-install <包名>` | 仅从本地 node_modules 执行 |
| `npx --ignore-existing <包名>` | 强制从远程获取 |
| `npx create-react-app my-app` | 创建 React 项目 |
| `npx degit user/repo dir` | 下载 GitHub 仓库（无需 git clone） |
| `npx serve .` | 启动静态文件服务器 |
| `npx http-server` | 另一款静态服务器 |
| `npx tsc --init` | 初始化 TypeScript 配置 |
| `npx prisma init` | 初始化 Prisma |
| `npx next dev` | 启动 Next.js 开发服务器 |

---

## 四、package.json 常用字段

| 字段 | 说明 |
|------|------|
| `name` | 包名 |
| `version` | 版本号 |
| `description` | 描述 |
| `main` | 入口文件（CommonJS） |
| `module` | ESM 入口文件 |
| `exports` | 条件导出（Node 12+） |
| `type: "module"` | 启用 ES Modules |
| `scripts` | 自定义脚本 |
| `dependencies` | 生产依赖 |
| `devDependencies` | 开发依赖 |
| `peerDependencies` | 同伴依赖 |
| `optionalDependencies` | 可选依赖 |
| `engines` | 指定 Node.js 版本要求 |
| `bin` | 可执行文件入口 |
| `files` | 发布时包含的文件列表 |
| `keywords` | 关键词 |
| `license` | 许可证 |
| `repository` | 仓库地址 |
| `bugs` | Bug 反馈地址 |
| `homepage` | 主页 |
| `private: true` | 防止意外发布 |

---

## 五、npm scripts 常用命令

| 命令 | 说明 |
|------|------|
| `npm run <脚本名>` | 运行自定义脚本 |
| `npm start` | 运行 start 脚本 |
| `npm test` | 运行 test 脚本 |
| `npm run build` | 构建项目 |
| `npm run dev` | 启动开发服务器 |
| `npm run lint` | 运行代码检查 |
| `npm run format` | 格式化代码 |
| `npm run preview` | 预览构建产物 |

### 常用脚本示例

```json
{
  "scripts": {
    "dev": "node --watch server.js",
    "start": "node server.js",
    "build": "vite build",
    "test": "vitest",
    "lint": "eslint .",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "prepare": "husky install"
  }
}
```

---

## 六、调试与性能

| 命令 | 说明 |
|------|------|
| `node --inspect-brk app.js` | 启动调试并在首行暂停 |
| `node inspect app.js` | 使用内置调试器 |
| `node --inspect=0.0.0.0:9229 app.js` | 允许远程调试 |
| `node --trace-deopt` | 跟踪 V8 去优化 |
| `node --trace-gc` | 跟踪垃圾回收 |
| `node --throw-deprecation` | 将弃用警告转为错误 |
| `node --pending-deprecation` | 显示所有待处理的弃用警告 |
| `node --experimental-loader <loader>` | 使用自定义 loader |
| `node --diagnostic-dir=<路径>` | 设置诊断输出目录 |
| `node --report-on-fatalerror` | 在致命错误时生成报告 |
| `node --report-on-signal` | 在收到信号时生成报告 |
| `node --report-compact` | 生成紧凑的报告 |

---

## 七、常用 Node.js 内置模块

| 模块 | 常用方法 | 说明 |
|------|----------|------|
| `fs` | `readFileSync`, `writeFileSync`, `existsSync`, `mkdirSync`, `readdirSync`, `watch` | 文件系统操作 |
| `path` | `join`, `resolve`, `basename`, `dirname`, `extname`, `parse`, `relative` | 路径处理 |
| `os` | `platform`, `arch`, `cpus`, `totalmem`, `freemem`, `homedir`, `hostname` | 操作系统信息 |
| `process` | `argv`, `env`, `cwd()`, `exit()`, `on('uncaughtException')`, `memoryUsage()` | 进程信息 |
| `http` / `https` | `createServer`, `request`, `get` | HTTP 服务器/客户端 |
| `url` | `parse`, `format`, `URL`, `URLSearchParams` | URL 解析 |
| `querystring` | `parse`, `stringify` | 查询字符串处理 |
| `crypto` | `randomBytes`, `createHash`, `createCipheriv`, `sign`, `verify` | 加密 |
| `child_process` | `exec`, `spawn`, `fork`, `execSync` | 子进程 |
| `events` | `EventEmitter` | 事件驱动 |
| `stream` | `Readable`, `Writable`, `Transform`, `Duplex`, `pipeline`, `finished` | 流处理 |
| `buffer` | `Buffer.from`, `Buffer.alloc`, `toString`, `concat` | 二进制数据 |
| `util` | `promisify`, `callbackify`, `types`, `deprecate`, `inspect` | 工具函数 |
| `assert` | `strict`, `ok`, `equal`, `deepEqual`, `throws`, `rejects` | 断言 |
| `timers` | `setTimeout`, `setInterval`, `setImmediate`, `clear*` | 定时器 |
| `cluster` | `fork`, `isMaster`, `isWorker`, `worker`, `workers` | 多进程 |
| `dns` | `lookup`, `resolve`, `reverse` | DNS 查询 |
| `net` | `createServer`, `connect`, `Socket` | TCP 网络 |
| `readline` | `createInterface`, `question` | 命令行交互 |
| `zlib` | `gzip`, `gunzip`, `deflate`, `inflate`, `brotliCompress` | 压缩 |
| `v8` | `getHeapStatistics`, `getHeapSpaceStatistics` | V8 引擎信息 |
| `performance` | `now()`, `mark()`, `measure()`, `getEntriesByType()` | 性能测量 |

---

## 八、常用第三方工具

| 工具 | 安装命令 | 用途 |
|------|----------|------|
| `nodemon` | `npm i -g nodemon` | 文件变化自动重启 |
| `ts-node` | `npm i -g ts-node` | 直接运行 TypeScript |
| `tsx` | `npm i -g tsx` | 更快的 TypeScript 执行器 |
| `pm2` | `npm i -g pm2` | 进程管理（守护、负载均衡） |
| `concurrently` | `npm i -g concurrently` | 并行运行多个命令 |
| `rimraf` | `npm i -g rimraf` | 跨平台 rm -rf |
| `cross-env` | `npm i -g cross-env` | 跨平台设置环境变量 |
| `serve` | `npm i -g serve` | 静态文件服务器 |
| `http-server` | `npm i -g http-server` | 轻量 HTTP 服务器 |
| `live-server` | `npm i -g live-server` | 带自动刷新的静态服务器 |
| `eslint` | `npm i -g eslint` | 代码检查 |
| `prettier` | `npm i -g prettier` | 代码格式化 |
| `husky` | `npm i -D husky` | Git hooks 工具 |
| `lint-staged` | `npm i -D lint-staged` | 仅对暂存文件运行 linter |
| `commitizen` | `npm i -g commitizen` | 规范化提交信息 |
| `standard-version` | `npm i -g standard-version` | 自动生成 changelog 和版本号 |
| `yarn` | `npm i -g yarn` | 替代 npm 的包管理器 |
| `pnpm` | `npm i -g pnpm` | 更快的包管理器（硬链接） |
| `bun` | `curl -fsSL https://bun.sh/install \| bash` | 高性能 JS 运行时 |
| `vite` | `npm i -g vite` | 前端构建工具 |
| `webpack` | `npm i -g webpack webpack-cli` | 模块打包器 |
| `rollup` | `npm i -g rollup` | ES Module 打包器 |
| `parcel` | `npm i -g parcel` | 零配置打包器 |
| `nx` | `npm i -g nx` | Monorepo 管理工具 |
| `turbo` | `npm i -g turbo` | 高性能 Monorepo 工具 |
| `lerna` | `npm i -g lerna` | 传统 Monorepo 工具 |
| `prisma` | `npm i -g prisma` | ORM 数据库工具 |
| `typeorm` | `npm i -g typeorm` | TypeScript ORM |
| `sequelize` | `npm i -g sequelize-cli` | SQL ORM CLI |
| `jest` | `npm i -g jest` | 测试框架 |
| `vitest` | `npm i -g vitest` | Vite 驱动的测试框架 |
| `mocha` | `npm i -g mocha` | 测试框架 |
| `cypress` | `npm i -g cypress` | 端到端测试 |
| `playwright` | `npm i -g playwright` | 浏览器自动化测试 |
| `swagger` | `npm i -g swagger-cli` | API 文档工具 |
| `graphql` | `npm i -g graphql-cli` | GraphQL CLI |
| `next` | `npm i -g create-next-app` | Next.js 项目脚手架 |
| `create-react-app` | `npm i -g create-react-app` | React 项目脚手架 |
| `vue` | `npm i -g @vue/cli` | Vue 项目脚手架 |
| `angular` | `npm i -g @angular/cli` | Angular 项目脚手架 |
| `nest` | `npm i -g @nestjs/cli` | NestJS 项目脚手架 |
| `express-generator` | `npm i -g express-generator` | Express 项目脚手架 |
| `strapi` | `npm i -g strapi` | Headless CMS |
| `keystone` | `npm i -g @keystone-6/core` | Headless CMS |
| `directus` | `npm i -g directus` | Headless CMS |
| `socket.io` | `npm i socket.io` | WebSocket 库 |
| `ws` | `npm i ws` | 轻量 WebSocket 库 |
| `axios` | `npm i axios` | HTTP 客户端 |
| `got` | `npm i got` | 现代 HTTP 客户端 |
| `undici` | `npm i undici` | Node.js 内置 HTTP 客户端的高性能替代 |
| `dayjs` | `npm i dayjs` | 轻量日期库 |
| `luxon` | `npm i luxon` | 强大日期库 |
| `moment` | `npm i moment` | 传统日期库（不再推荐） |
| `lodash` | `npm i lodash` | 实用工具函数库 |
| `ramda` | `npm i ramda` | 函数式编程库 |
| `immer` | `npm i immer` | 不可变数据结构 |
| `zod` | `npm i zod` | 模式验证 |
| `joi` | `npm i joi` | 对象模式验证 |
| `yup` | `npm i yup` | 模式验证（常用于表单） |
| `dotenv` | `npm i dotenv` | 加载 .env 文件 |
| `config` | `npm i config` | 配置管理 |
| `winston` | `npm i winston` | 日志库 |
| `pino` | `npm i pino` | 高性能日志库 |
| `morgan` | `npm i morgan` | HTTP 请求日志中间件 |
| `helmet` | `npm i helmet` | 安全中间件 |
| `cors` | `npm i cors` | CORS 中间件 |
| `compression` | `npm i compression` | 压缩中间件 |
| `multer` | `npm i multer` | 文件上传中间件 |
| `bcrypt` | `npm i bcrypt` | 密码哈希 |
| `jsonwebtoken` | `npm i jsonwebtoken` | JWT 令牌 |
| `passport` | `npm i passport` | 认证中间件 |
| `sharp` | `npm i sharp` | 图像处理 |
| `cheerio` | `npm i cheerio` | HTML 解析 |
| `puppeteer` | `npm i puppeteer` | 无头浏览器 |
| `playwright` | `npm i playwright` | 浏览器自动化 |
| `bull` | `npm i bull` | 任务队列（基于 Redis） |
| `agenda` | `npm i agenda` | 任务调度 |
| `node-cron` | `npm i node-cron` | Cron 任务 |
| `socket.io` | `npm i socket.io` | WebSocket |
| `mqtt` | `npm i mqtt` | MQTT 客户端 |
| `amqplib` | `npm i amqplib` | RabbitMQ 客户端 |
| `kafkajs` | `npm i kafkajs` | Kafka 客户端 |
| `redis` | `npm i redis` | Redis 客户端 |
| `ioredis` | `npm i ioredis` | 高性能 Redis 客户端 |
| `mongoose` | `npm i mongoose` | MongoDB ODM |
| `mongodb` | `npm i mongodb` | MongoDB 驱动 |
| `pg` | `npm i pg` | PostgreSQL 驱动 |
| `mysql2` | `npm i mysql2` | MySQL 驱动 |
| `better-sqlite3` | `npm i better-sqlite3` | SQLite 驱动 |
| `knex` | `npm i knex` | SQL 查询构建器 |
| `drizzle-orm` | `npm i drizzle-orm` | TypeScript ORM |
| `graphql-yoga` | `npm i graphql-yoga` | GraphQL 服务器 |
| `apollo-server` | `npm i apollo-server` | GraphQL 服务器 |
| `trpc` | `npm i @trpc/server` | 类型安全 API |

---

## 九、实用技巧

1. **查看 Node.js 文档（命令行）**  
   ```bash
   node -e "console.log(require('fs').readFileSync)"
   # 或使用 man 查看（macOS/Linux 需安装）
   man node
   ```

2. **快速启动 REPL 并加载模块**  
   ```bash
   node -i -e "const fs = require('fs')"
   ```

3. **运行 ES Module 文件**  
   ```bash
   node --experimental-modules app.mjs
   # 或在 package.json 中设置 "type": "module"
   ```

4. **使用 --watch 自动重启（Node 18+）**  
   ```bash
   node --watch app.js
   ```

5. **调试 Node.js 应用**  
   ```bash
   node --inspect-brk app.js
   # 然后在 Chrome 打开 chrome://inspect
   ```

6. **查看全局安装的包**  
   ```bash
   npm list -g --depth=0
   ```

7. **查看某个包的最新版本**  
   ```bash
   npm view <包名> version
   npm view <包名> versions
   npm view <包名> dist-tags
   ```

8. **查看包的依赖关系**  
   ```bash
   npm ll <包名>
   npm ls <包名>
   ```

9. **清除 npm 缓存**  
   ```bash
   npm cache clean --force
   ```

10. **修复 npm 权限问题（Linux/Mac）**  
    ```bash
    sudo chown -R $(whoami) ~/.npm
    ```

11. **使用 nvm 管理 Node.js 版本**  
    ```bash
    nvm install 20           # 安装 Node 20
    nvm use 20               # 切换到 Node 20
    nvm alias default 20     # 设置默认版本
    nvm ls                   # 列出已安装版本
    nvm current              # 查看当前版本
    ```

12. **使用 fnm 更快的版本管理器**  
    ```bash
    fnm install 20
    fnm use 20
    fnm default 20
    ```

13. **检查 package.json 中的脚本**  
    ```bash
    node -e "console.log(Object.keys(require('./package.json').scripts).join('\n'))"
    ```

14. **在 package.json 中使用环境变量（cross-env）**  
    ```json
    {
      "scripts": {
        "build": "cross-env NODE_ENV=production webpack"
      }
    }
    ```

15. **查看进程内存使用**  
    ```bash
    node -e "console.log(process.memoryUsage())"
    ```

16. **查看 V8 堆统计**  
    ```bash
    node -e "console.log(require('v8').getHeapStatistics())"
    ```

17. **测试网络连通性（内置）**  
    ```bash
    node -e "require('http').get('http://example.com', res => console.log(res.statusCode))"
    ```

18. **生成随机密码**  
    ```bash
    node -e "console.log(require('crypto').randomBytes(16).toString('hex'))"
    ```

19. **计算文件哈希**  
    ```bash
    node -e "const fs=require('fs'), crypto=require('crypto'); const hash=crypto.createHash('sha256'); fs.createReadStream('file.txt').pipe(hash).on('finish',()=>console.log(hash.digest('hex')))"
    ```

20. **使用 util.promisify 将回调转为 Promise**  
    ```bash
    node -e "const { promisify } = require('util'); const readFile = promisify(require('fs').readFile); readFile('file.txt','utf8').then(console.log)"
    ```

21. **查看 Node.js 支持的 ES 特性**  
    ```bash
    node --v8-options | grep harmony
    ```

22. **使用 --experimental-vm-modules 运行 VM 模块**  
    ```bash
    node --experimental-vm-modules script.js
    ```

23. **在 Windows 上设置 NODE_ENV**  
    ```powershell
    $env:NODE_ENV="production"; node app.js
    # 或使用 cross-env
    ```

24. **使用 npm link 本地调试包**  
    ```bash
    cd my-package
    npm link
    cd ../my-project
    npm link my-package
    ```

25. **使用 npm unlink 解除本地链接**  
    ```bash
    cd my-project
    npm unlink my-package
    cd ../my-package
    npm unlink
    ```

26. **查看 npm 脚本的执行顺序**  
    ```bash
    npm run build --scripts-prepend-node-path
    ```

27. **使用 npx 临时使用不同版本的 Node**  
    ```bash
    npx node@18 -e "console.log(process.version)"
    ```

28. **使用 --experimental-json-modules 导入 JSON（旧版本）**  
    ```bash
    node --experimental-json-modules app.mjs
    ```

29. **查看 Node.js 的默认搜索路径**  
    ```bash
    node -e "console.log(module.paths)"
    ```

30. **使用 process.nextTick 与 setImmediate 的区别**  
    ```bash
    node -e "setImmediate(()=>console.log('immediate')); process.nextTick(()=>console.log('nextTick')); console.log('sync')"
    # 输出: sync -> nextTick -> immediate
    ```

---

> **提示**：Node.js 生态更新迅速，建议定期关注 Node.js 官方博客（nodejs.org/en/blog）和 npm 官方文档。使用 `node --help` 查看所有命令行选项，使用 `npm help <命令>` 查看 npm 子命令的帮助。