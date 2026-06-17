# Python 常用命令速查手册

> 适用版本：Python 3.8+，部分命令在 Python 3.12+ 可能有细微变化。

---

## 一、Python 解释器与环境

| 命令 | 说明 |
|------|------|
| `python --version` | 查看 Python 版本 |
| `python -c "print('hello')"` | 直接执行单行代码 |
| `python -m <模块名>` | 以脚本方式运行模块（如 `python -m http.server`） |
| `python -i <脚本.py>` | 运行脚本后进入交互模式 |
| `python -B` | 不生成 `__pycache__` 目录 |
| `python -OO` | 优化模式（移除 assert 和 docstring） |
| `python -X dev` | 开发者模式（更详细的警告） |
| `python -X utf8` | 默认使用 UTF-8 编码（Python 3.15+ 默认） |
| `python -v` | 详细模式（显示 import 过程） |
| `python -W ignore::DeprecationWarning` | 忽略特定警告 |
| `where python` (Windows) / `which python` (Linux/Mac) | 查看 Python 可执行文件路径 |

---

## 二、虚拟环境管理

| 命令 | 说明 |
|------|------|
| `python -m venv <目录名>` | 创建虚拟环境 |
| `python -m venv --system-site-packages <目录名>` | 创建虚拟环境并继承系统包 |
| `<venv>\Scripts\activate` (Windows) | 激活虚拟环境（cmd） |
| `source <venv>/bin/activate` (Linux/Mac) | 激活虚拟环境 |
| `deactivate` | 退出虚拟环境 |
| `pip list` | 查看当前环境已安装的包 |
| `pip freeze > requirements.txt` | 导出当前环境的包列表 |
| `pip install -r requirements.txt` | 根据文件安装依赖 |

### 使用 `uv`（更快的替代品）

| 命令 | 说明 |
|------|------|
| `uv venv` | 创建虚拟环境 |
| `uv pip install <包>` | 安装包 |
| `uv pip sync requirements.txt` | 同步依赖 |
| `uv tool run <工具名>` | 运行工具（类似 npx） |

---

## 三、包管理（pip）

| 命令 | 说明 |
|------|------|
| `pip install <包名>` | 安装包（最新版） |
| `pip install <包名>==版本` | 安装指定版本 |
| `pip install <包名>>=版本,<版本` | 安装版本范围 |
| `pip install --upgrade <包名>` | 升级包 |
| `pip install --user <包名>` | 安装到用户目录（无需管理员） |
| `pip uninstall <包名>` | 卸载包 |
| `pip list` | 列出已安装包 |
| `pip list --outdated` | 列出有过期更新的包 |
| `pip show <包名>` | 查看包的详细信息 |
| `pip search <关键词>` | 搜索 PyPI 上的包（PyPI 已禁用，改用浏览器） |
| `pip download <包名> -d <目录>` | 下载包但不安装 |
| `pip cache list` | 查看 pip 缓存 |
| `pip cache purge` | 清空 pip 缓存 |
| `pip check` | 检查依赖冲突 |
| `pip install -e .` | 以可编辑模式安装当前项目（开发模式） |
| `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>` | 使用国内镜像源 |

### 常用镜像源

```
清华: https://pypi.tuna.tsinghua.edu.cn/simple
阿里: https://mirrors.aliyun.com/pypi/simple/
中科大: https://pypi.mirrors.ustc.edu.cn/simple/
豆瓣: https://pypi.doubanio.com/simple/
```

### 配置默认镜像源

```bash
# 全局配置（Linux/Mac）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Windows
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 四、常用内置函数与标准库

| 命令/函数 | 说明 |
|-----------|------|
| `len(obj)` | 返回长度 |
| `type(obj)` | 返回类型 |
| `dir(obj)` | 返回对象的属性和方法列表 |
| `help(obj)` | 打开帮助文档 |
| `str()`, `int()`, `float()`, `bool()` | 类型转换 |
| `range(start, stop, step)` | 生成整数序列 |
| `enumerate(iterable, start=0)` | 枚举索引和值 |
| `zip(*iterables)` | 并行迭代多个可迭代对象 |
| `map(func, iterable)` | 对每个元素应用函数 |
| `filter(func, iterable)` | 过滤元素 |
| `sorted(iterable, key=None, reverse=False)` | 排序 |
| `reversed(seq)` | 反转序列 |
| `any(iterable)` / `all(iterable)` | 逻辑判断 |
| `sum(iterable, start=0)` | 求和 |
| `min(iterable)` / `max(iterable)` | 最小值/最大值 |
| `abs(x)` | 绝对值 |
| `round(x, ndigits)` | 四舍五入 |
| `divmod(a, b)` | 返回 (a//b, a%b) |
| `pow(x, y, mod)` | 幂运算（可带模） |
| `ord(char)` / `chr(int)` | 字符与 Unicode 码互转 |
| `repr(obj)` | 返回对象的“官方”字符串表示 |
| `eval(expr)` | 执行字符串表达式（**慎用**） |
| `exec(code)` | 执行字符串代码（**慎用**） |
| `open(file, mode='r', encoding='utf-8')` | 打开文件 |
| `with open(...) as f:` | 上下文管理器打开文件 |
| `input(prompt)` | 读取用户输入 |
| `print(*objects, sep=' ', end='\n', file=sys.stdout)` | 打印输出 |
| `format(value, spec)` | 格式化字符串 |
| `isinstance(obj, classinfo)` | 检查对象类型 |
| `hasattr(obj, name)` | 检查对象是否有属性 |
| `getattr(obj, name, default)` | 获取对象属性 |
| `setattr(obj, name, value)` | 设置对象属性 |
| `__name__` | 模块名（`__main__` 表示直接运行） |

---

## 五、文件与路径操作

| 命令 | 说明 |
|------|------|
| `open('file.txt', 'r').read()` | 读取整个文件 |
| `open('file.txt', 'r').readlines()` | 按行读取 |
| `open('file.txt', 'w').write('内容')` | 写入文件（覆盖） |
| `open('file.txt', 'a').write('内容')` | 追加写入 |
| `os.listdir(path)` | 列出目录内容 |
| `os.path.join(path, *paths)` | 拼接路径 |
| `os.path.exists(path)` | 判断路径是否存在 |
| `os.path.isfile(path)` | 判断是否为文件 |
| `os.path.isdir(path)` | 判断是否为目录 |
| `os.path.abspath(path)` | 获取绝对路径 |
| `os.path.dirname(path)` | 获取目录名 |
| `os.path.basename(path)` | 获取文件名 |
| `os.path.splitext(path)` | 分离文件名和扩展名 |
| `os.makedirs(path, exist_ok=True)` | 递归创建目录 |
| `os.remove(path)` | 删除文件 |
| `os.rmdir(path)` | 删除空目录 |
| `shutil.rmtree(path)` | 递归删除目录树 |
| `shutil.copy(src, dst)` | 复制文件 |
| `shutil.copytree(src, dst)` | 复制目录树 |
| `glob.glob('模式')` | 通配符匹配文件 |
| `pathlib.Path(path)` | 面向对象的路径操作（推荐） |

### Pathlib 示例

```python
from pathlib import Path

p = Path('/home/user/file.txt')
p.name          # 'file.txt'
p.stem          # 'file'
p.suffix        # '.txt'
p.parent        # PosixPath('/home/user')
p.exists()
p.is_file()
p.read_text()
p.write_text('内容')
p.iterdir()     # 遍历目录
p.mkdir(parents=True, exist_ok=True)
```

---

## 六、调试与测试

| 命令 | 说明 |
|------|------|
| `breakpoint()` | 进入调试器（Python 3.7+） |
| `python -m pdb <脚本.py>` | 使用 pdb 调试 |
| `python -m trace --trace <脚本.py>` | 跟踪代码执行 |
| `python -m cProfile <脚本.py>` | 性能分析 |
| `python -m timeit '代码'` | 测量代码执行时间 |
| `python -m unittest discover` | 运行单元测试 |
| `python -m pytest` | 运行 pytest（需安装） |
| `assert 条件, "错误信息"` | 断言 |
| `logging.debug/info/warning/error(msg)` | 日志输出 |
| `print(f"var={var}", file=sys.stderr)` | 打印到 stderr |

---

## 七、代码检查与格式化

| 命令 | 说明 |
|------|------|
| `python -m py_compile <脚本.py>` | 检查语法（不运行） |
| `python -m compileall <目录>` | 批量编译 .pyc |
| `flake8 <文件或目录>` | 代码风格检查（需安装 flake8） |
| `pylint <文件或目录>` | 更严格的代码检查 |
| `black <文件或目录>` | 自动格式化代码 |
| `isort <文件或目录>` | 排序 import 语句 |
| `mypy <文件或目录>` | 静态类型检查 |
| `ruff check <文件或目录>` | Rust 实现的快速 lint 工具 |
| `ruff format <文件或目录>` | Ruff 格式化 |

---

## 八、构建与打包

| 命令 | 说明 |
|------|------|
| `python setup.py sdist bdist_wheel` | 构建源码包和 wheel 包 |
| `python -m build` | 使用 build 模块构建（推荐） |
| `twine upload dist/*` | 上传到 PyPI（需安装 twine） |
| `pip install build twine` | 安装构建工具 |
| `python -m pip install --editable .` | 开发模式安装 |

---

## 九、常用第三方工具

| 工具 | 安装命令 | 用途 |
|------|----------|------|
| `requests` | `pip install requests` | HTTP 请求 |
| `httpx` | `pip install httpx` | 现代 HTTP 客户端（支持 async） |
| `fastapi` | `pip install fastapi uvicorn` | Web API 框架 |
| `flask` | `pip install flask` | 轻量 Web 框架 |
| `django` | `pip install django` | 全栈 Web 框架 |
| `pandas` | `pip install pandas` | 数据处理 |
| `numpy` | `pip install numpy` | 数值计算 |
| `matplotlib` | `pip install matplotlib` | 数据可视化 |
| `jupyter` | `pip install jupyter` | 交互式笔记本 |
| `jupyter lab` | `pip install jupyterlab` | JupyterLab 界面 |
| `streamlit` | `pip install streamlit` | 快速构建数据应用 |
| `rich` | `pip install rich` | 终端富文本输出 |
| `tqdm` | `pip install tqdm` | 进度条 |
| `click` | `pip install click` | 命令行参数解析 |
| `typer` | `pip install typer` | 基于类型注解的 CLI 工具 |
| `pydantic` | `pip install pydantic` | 数据验证与设置管理 |
| `sqlalchemy` | `pip install sqlalchemy` | ORM 框架 |
| `beautifulsoup4` | `pip install beautifulsoup4` | HTML/XML 解析 |
| `selenium` | `pip install selenium` | 浏览器自动化 |
| `playwright` | `pip install playwright` | 新一代浏览器自动化 |
| `celery` | `pip install celery` | 异步任务队列 |
| `redis` | `pip install redis` | Redis 客户端 |
| `pymongo` | `pip install pymongo` | MongoDB 客户端 |
| `psycopg2` | `pip install psycopg2-binary` | PostgreSQL 驱动 |
| `asyncpg` | `pip install asyncpg` | 异步 PostgreSQL 驱动 |
| `aiomysql` | `pip install aiomysql` | 异步 MySQL 驱动 |
| `motor` | `pip install motor` | 异步 MongoDB 驱动 |

---

## 十、实用技巧

1. **启动简易 HTTP 服务器**  
   ```bash
   python -m http.server 8000
   ```

2. **启动 SMTP 调试服务器**  
   ```bash
   python -m smtpd -n -c DebuggingServer localhost:1025
   ```

3. **JSON 格式化输出**  
   ```bash
   echo '{"name":"test"}' | python -m json.tool
   ```

4. **Base64 编解码**  
   ```bash
   echo -n "hello" | python -m base64
   ```

5. **URL 编解码**  
   ```bash
   python -c "import urllib.parse; print(urllib.parse.quote('你好'))"
   ```

6. **计算文件哈希**  
   ```bash
   python -c "import hashlib; print(hashlib.md5(open('file','rb').read()).hexdigest())"
   ```

7. **查看 Python 搜索路径**  
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

8. **查看所有内置模块**  
   ```bash
   python -c "import sys; print('\n'.join(sys.builtin_module_names))"
   ```

9. **生成 UUID**  
   ```bash
   python -c "import uuid; print(uuid.uuid4())"
   ```

10. **快速 CSV 查看**  
    ```bash
    python -c "import csv, sys; reader=csv.reader(sys.stdin); [print(row) for row in reader]" < file.csv
    ```

11. **测量代码执行时间（timeit）**  
    ```bash
    python -m timeit -s "import math" "math.sqrt(2)"
    ```

12. **性能分析（cProfile）**  
    ```bash
    python -m cProfile -s cumulative my_script.py
    ```

13. **调试器（pdb）常用命令**  
    ```
    n (next)        # 执行下一行
    s (step)        # 进入函数
    c (continue)    # 继续执行到断点
    l (list)        # 显示当前行周围代码
    p var           # 打印变量值
    pp var          # 漂亮打印
    q (quit)        # 退出调试器
    ```

14. **交互模式下查看模块内容**  
    ```python
    import os
    dir(os)
    help(os.path.join)
    ```

15. **清理 `__pycache__` 目录**  
    ```bash
    find . -type d -name "__pycache__" -exec rm -rf {} +
    # 或使用 pyclean（需安装）
    pip install pyclean
    pyclean .
    ```

16. **使用 `-u` 强制无缓冲输出（实时日志）**  
    ```bash
    python -u script.py
    ```

17. **使用 `-bb` 启用 bytes 警告**  
    ```bash
    python -bb script.py
    ```

18. **查看已安装包的许可证**  
    ```bash
    pip list --format=columns | awk '{print $1}' | xargs pip show | grep -E "Name:|License:"
    ```

19. **导出所有已安装包的版本到文件**  
    ```bash
    pip freeze > requirements.txt
    ```

20. **根据 requirements.txt 重建环境**  
    ```bash
    python -m venv new_env
    source new_env/bin/activate
    pip install -r requirements.txt
    ```

---

> **提示**：Python 生态非常庞大，以上仅列出日常开发中最常用的部分。遇到问题时，善用 `help()` 函数和官方文档（docs.python.org）。对于第三方库，可访问 PyPI 官网或 `pip show <包名>` 查看详细信息。