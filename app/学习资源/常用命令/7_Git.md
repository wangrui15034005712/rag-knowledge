# Git 常用命令速查手册

> 适用版本：Git 2.x，大部分命令向下兼容。

---

## 一、配置

| 命令 | 说明 |
|------|------|
| `git config --global user.name "名字"` | 设置全局用户名 |
| `git config --global user.email "邮箱"` | 设置全局邮箱 |
| `git config --global core.editor vim` | 设置默认编辑器 |
| `git config --global init.defaultBranch main` | 设置默认分支名为 main |
| `git config --global alias.别名 命令` | 设置别名（如 `alias.co checkout`） |
| `git config --global color.ui auto` | 启用颜色输出 |
| `git config --list` | 查看所有配置 |
| `git config --global --unset 键` | 删除某项配置 |
| `git config --global credential.helper store` | 存储凭证（免密一段时间） |
| `git config --global core.autocrlf input` | 处理换行符（Linux/Mac） |

---

## 二、创建与克隆仓库

| 命令 | 说明 |
|------|------|
| `git init` | 在当前目录初始化 Git 仓库 |
| `git clone <仓库地址>` | 克隆远程仓库到本地 |
| `git clone <仓库地址> <目录名>` | 克隆到指定目录 |
| `git clone --depth=1 <仓库地址>` | 浅克隆（只拉取最新版本，加快速度） |
| `git clone --recursive <仓库地址>` | 克隆并初始化子模块 |

---

## 三、基本操作（暂存区与提交）

| 命令 | 说明 |
|------|------|
| `git status` | 查看工作区状态 |
| `git status -s` | 简洁状态（M 修改，A 添加，?? 未跟踪） |
| `git add <文件>` | 将文件加入暂存区 |
| `git add .` | 将所有变动加入暂存区 |
| `git add -A` | 等同 git add .，包括删除 |
| `git add -p` | 交互式选择每一块变更是否暂存 |
| `git restore <文件>` | 丢弃工作区的修改（未暂存时） |
| `git restore --staged <文件>` | 将文件移出暂存区（保留工作区修改） |
| `git commit -m "提交信息"` | 提交暂存区内容 |
| `git commit -am "提交信息"` | 跳过 git add，直接提交已跟踪文件的修改 |
| `git commit --amend -m "新信息"` | 修改最近一次提交的信息 |
| `git commit --amend --no-edit` | 修改最近一次提交（不改信息，可用于补充文件） |
| `git reset HEAD <文件>` | 旧版用法：将文件移出暂存区（新版推荐 restore） |
| `git rm <文件>` | 删除文件并加入暂存区 |
| `git mv <旧名> <新名>` | 重命名文件并加入暂存区 |

---

## 四、查看历史

| 命令 | 说明 |
|------|------|
| `git log` | 查看提交历史 |
| `git log --oneline` | 简洁版（一行一个提交） |
| `git log --graph --oneline --decorate` | 图形化分支历史 |
| `git log -p` | 显示每次提交的 diff |
| `git log --stat` | 显示每次提交的文件变更统计 |
| `git log --author="名字"` | 按作者过滤 |
| `git log --since="2024-01-01"` | 按时间过滤 |
| `git log --grep="关键词"` | 按提交信息搜索 |
| `git log -S "字符串"` | 按代码内容搜索（pickaxe） |
| `git log <文件>` | 查看某个文件的提交历史 |
| `git blame <文件>` | 逐行显示最后修改者和提交 |
| `git reflog` | 查看所有 HEAD 移动记录（找回丢失的提交） |
| `git shortlog -sn` | 统计每位作者的提交次数 |

---

## 五、分支管理

| 命令 | 说明 |
|------|------|
| `git branch` | 列出本地分支（当前分支前有 *） |
| `git branch -a` | 列出所有分支（含远程） |
| `git branch -r` | 列出远程分支 |
| `git branch <分支名>` | 创建新分支（停留在当前分支） |
| `git switch <分支名>` | 切换到已有分支 |
| `git switch -c <分支名>` | 创建并切换到新分支 |
| `git checkout <分支名>` | 旧版切换分支 |
| `git checkout -b <分支名>` | 旧版创建并切换 |
| `git branch -d <分支名>` | 删除已合并的分支 |
| `git branch -D <分支名>` | 强制删除未合并的分支 |
| `git branch -m <旧名> <新名>` | 重命名分支 |
| `git merge <分支名>` | 将指定分支合并到当前分支 |
| `git merge --no-ff <分支名>` | 禁用快进合并（保留分支历史） |
| `git rebase <分支名>` | 变基：将当前分支的提交移植到目标分支顶端 |
| `git rebase -i HEAD~N` | 交互式变基：合并/修改/重排最近 N 个提交 |
| `git cherry-pick <提交哈希>` | 将某个提交应用到当前分支 |

---

## 六、远程仓库

| 命令 | 说明 |
|------|------|
| `git remote -v` | 查看远程仓库地址 |
| `git remote add <别名> <URL>` | 添加远程仓库 |
| `git remote remove <别名>` | 删除远程仓库 |
| `git remote rename <旧名> <新名>` | 重命名远程仓库 |
| `git remote set-url <别名> <新URL>` | 修改远程仓库地址 |
| `git fetch <远程名>` | 拉取远程分支信息（不自动合并） |
| `git fetch --prune` | 拉取并清理本地已删除的远程分支引用 |
| `git pull` | 拉取并合并（相当于 fetch + merge） |
| `git pull --rebase` | 拉取并变基（推荐，保持线性历史） |
| `git push` | 推送当前分支到远程同名分支 |
| `git push origin <分支名>` | 推送指定分支到远程 |
| `git push -u origin <分支名>` | 推送并建立上游关联（首次推送） |
| `git push origin --delete <分支名>` | 删除远程分支 |
| `git push --tags` | 推送所有标签 |
| `git push --force` | 强制推送（**慎用**，会覆盖远程历史） |
| `git push --force-with-lease` | 更安全的强制推送（检查远程是否有新提交） |

---

## 七、标签

| 命令 | 说明 |
|------|------|
| `git tag` | 列出所有标签 |
| `git tag -l "模式"` | 按模式搜索标签（如 `v1.*`） |
| `git tag <标签名>` | 创建轻量标签（指向当前提交） |
| `git tag -a <标签名> -m "说明"` | 创建附注标签 |
| `git tag -a <标签名> <提交哈希> -m "说明"` | 为历史提交创建标签 |
| `git show <标签名>` | 查看标签详情 |
| `git tag -d <标签名>` | 删除本地标签 |
| `git push origin <标签名>` | 推送单个标签到远程 |
| `git push origin --tags` | 推送所有标签 |
| `git push origin --delete tag <标签名>` | 删除远程标签 |

---

## 八、贮藏（Stash）

| 命令 | 说明 |
|------|------|
| `git stash` | 将工作区修改暂存，恢复干净工作区 |
| `git stash push -m "说明"` | 暂存并添加描述 |
| `git stash list` | 查看所有贮藏列表 |
| `git stash apply` | 应用最近的贮藏（不移除） |
| `git stash pop` | 应用最近的贮藏并移除 |
| `git stash drop` | 删除最近的贮藏 |
| `git stash clear` | 清空所有贮藏 |
| `git stash show -p` | 查看贮藏内容的 diff |

---

## 九、比较差异

| 命令 | 说明 |
|------|------|
| `git diff` | 工作区 vs 暂存区 |
| `git diff --staged` | 暂存区 vs 最近一次提交 |
| `git diff HEAD` | 工作区 vs 最近一次提交 |
| `git diff <分支1> <分支2>` | 比较两个分支 |
| `git diff <提交1> <提交2>` | 比较两个提交 |
| `git diff --word-diff` | 按单词显示差异 |
| `git difftool` | 使用外部工具查看差异 |

---

## 十、撤销与恢复

| 命令 | 说明 |
|------|------|
| `git restore <文件>` | 丢弃工作区修改 |
| `git restore --staged <文件>` | 取消暂存 |
| `git reset --soft HEAD~1` | 撤销最近一次提交，保留工作区和暂存区 |
| `git reset --mixed HEAD~1` | 撤销最近一次提交，保留工作区（默认） |
| `git reset --hard HEAD~1` | 撤销最近一次提交，**丢弃所有修改** |
| `git revert <提交哈希>` | 创建一个新提交来抵消指定提交的更改 |
| `git clean -fd` | 删除所有未跟踪的文件和目录 |
| `git clean -nd` | 预览将要删除的文件（安全演练） |
| `git checkout -- <文件>` | 旧版：丢弃工作区修改 |

---

## 十一、子模块

| 命令 | 说明 |
|------|------|
| `git submodule add <仓库地址> <路径>` | 添加子模块 |
| `git submodule init` | 初始化子模块配置 |
| `git submodule update` | 拉取子模块内容 |
| `git submodule update --init --recursive` | 完整初始化并更新所有子模块 |
| `git submodule foreach git pull` | 对所有子模块执行命令 |
| `git submodule deinit <路径>` | 卸载子模块 |

---

## 十二、高级与杂项

| 命令 | 说明 |
|------|------|
| `git bisect start` | 二分查找引入 bug 的提交 |
| `git bisect bad` | 标记当前提交为坏 |
| `git bisect good <提交>` | 标记某提交为好 |
| `git bisect reset` | 结束 bisect |
| `git grep "关键词"` | 在工作区搜索文本 |
| `git archive -o output.zip HEAD` | 将当前版本打包为 zip |
| `git worktree add <路径> <分支>` | 创建新的工作目录指向另一个分支 |
| `git gc` | 垃圾回收，优化仓库 |
| `git fsck` | 检查仓库完整性 |
| `git verify-pack` | 检查 pack 文件 |
| `git count-objects -v` | 查看仓库对象统计 |

---

## 十三、实用技巧

1. **查看某行代码是谁写的**  
   ```bash
   git blame -L 10,20 文件名
   ```

2. **查找包含某字符串的提交**  
   ```bash
   git log -S "待搜索字符串" --source --all
   ```

3. **恢复被删除的分支（通过 reflog）**  
   ```bash
   git reflog                     # 找到丢失分支的最后一次提交哈希
   git checkout -b 新分支名 <哈希>
   ```

4. **只提交部分文件的某几行**  
   ```bash
   git add -p 文件名
   ```

5. **将多个提交合并为一个**  
   ```bash
   git rebase -i HEAD~3           # 将最近3个提交合并
   # 在编辑器中将 pick 改为 squash 或 fixup
   ```

6. **清理本地已删除的远程分支引用**  
   ```bash
   git remote prune origin
   ```

7. **忽略已跟踪文件的修改（本地生效）**  
   ```bash
   git update-index --assume-unchanged 文件名
   git update-index --no-assume-unchanged 文件名  # 恢复
   ```

8. **查看某个文件的修改历史（逐行）**  
   ```bash
   git log --follow -p 文件名
   ```

9. **暂存并跳过 pre-commit hook**  
   ```bash
   git commit --no-verify -m "信息"
   ```

10. **将当前分支的某次提交复制到另一个分支**  
    ```bash
    git cherry-pick <提交哈希>
    ```

11. **对比两个分支的文件列表**  
    ```bash
    git diff --name-status main..feature
    ```

12. **查看最近一次提交的变更文件列表**  
    ```bash
    git show --stat
    ```

13. **修改历史提交的作者信息**  
    ```bash
    git commit --amend --author="新作者 <email>" --no-edit
    ```

14. **批量删除本地已合并的分支**  
    ```bash
    git branch --merged | grep -v "\*\|main\|master" | xargs -n 1 git branch -d
    ```

15. **设置 Git 代理（用于某些网络环境）**  
    ```bash
    git config --global http.proxy http://127.0.0.1:7890
    git config --global https.proxy http://127.0.0.1:7890
    # 取消代理
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    ```

---

> **提示**：Git 命令非常丰富，以上仅覆盖日常开发中最常用的部分。遇到不确定的命令时，使用 `git help <命令>` 查看完整手册，或 `git <命令> --help` 打开浏览器文档。