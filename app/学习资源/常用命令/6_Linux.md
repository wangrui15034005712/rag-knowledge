# Linux 常用命令速查手册

> 适用于大多数 Linux 发行版（CentOS / Ubuntu / Debian / Rocky 等），部分命令可能需要安装对应软件包。

---

## 一、文件与目录操作

| 命令 | 说明 |
|------|------|
| `ls -la` | 列出当前目录所有文件（含隐藏文件、详细信息） |
| `ll` | 多数发行版中 `ls -l` 的别名 |
| `cd <目录>` | 切换目录 |
| `pwd` | 显示当前工作目录 |
| `mkdir -p <目录>` | 递归创建目录 |
| `rmdir <目录>` | 删除空目录 |
| `rm -rf <文件/目录>` | 强制递归删除（**谨慎使用**） |
| `cp -r <源> <目标>` | 递归复制目录 |
| `mv <源> <目标>` | 移动或重命名 |
| `touch <文件>` | 创建空文件或更新文件时间戳 |
| `cat <文件>` | 查看文件内容 |
| `less <文件>` | 分页查看文件（按 q 退出） |
| `more <文件>` | 分页查看（空格翻页，Enter 下一行） |
| `head -n 行数 <文件>` | 查看文件开头 N 行 |
| `tail -n 行数 <文件>` | 查看文件末尾 N 行 |
| `tail -f <文件>` | 实时跟踪文件增长（常用于查看日志） |
| `find <路径> -name "模式"` | 查找文件 |
| `locate <关键词>` | 快速搜索文件（需先运行 updatedb） |
| `which <命令>` | 查看命令的可执行文件路径 |
| `whereis <命令>` | 查看命令的二进制、源码、man 页位置 |
| `tree <目录>` | 以树形显示目录结构（需安装 tree） |
| `du -sh <文件/目录>` | 查看文件或目录的磁盘占用 |
| `df -h` | 查看磁盘分区使用情况 |
| `ln -s <目标> <链接名>` | 创建软链接 |
| `stat <文件>` | 查看文件的详细信息（inode、时间戳等） |

---

## 二、文件权限与归属

| 命令 | 说明 |
|------|------|
| `chmod 755 <文件>` | 设置权限（rwxr-xr-x） |
| `chmod u+x <文件>` | 给所有者增加可执行权限 |
| `chown <用户>:<组> <文件>` | 修改文件所有者和所属组 |
| `chgrp <组> <文件>` | 修改文件所属组 |
| `umask` | 查看或设置默认权限掩码 |
| `getfacl <文件>` | 查看文件的 ACL 权限 |
| `setfacl -m u:用户:权限 <文件>` | 设置 ACL 权限 |

---

## 三、文本处理

| 命令 | 说明 |
|------|------|
| `grep "模式" <文件>` | 搜索文本 |
| `grep -r "模式" <目录>` | 递归搜索目录 |
| `grep -v "模式"` | 排除匹配行 |
| `grep -i "模式"` | 忽略大小写 |
| `sed 's/旧/新/g' <文件>` | 替换文本（输出到 stdout） |
| `sed -i 's/旧/新/g' <文件>` | 原地替换 |
| `awk '{print $1}' <文件>` | 按空格分割，打印第一列 |
| `awk -F':' '{print $1,$3}'` | 指定分隔符为冒号 |
| `sort <文件>` | 排序 |
| `sort -n` | 按数值排序 |
| `sort -r` | 逆序排序 |
| `uniq` | 去除连续重复行（常与 sort 配合） |
| `wc -l` | 统计行数 |
| `wc -w` | 统计单词数 |
| `cut -d',' -f1 <文件>` | 按逗号分割取第一列 |
| `tr 'a-z' 'A-Z'` | 字符转换（小写转大写） |
| `diff <文件1> <文件2>` | 比较两个文件差异 |
| `comm <文件1> <文件2>` | 比较两个已排序文件的公共行 |
| `paste <文件1> <文件2>` | 按列合并文件 |
| `join <文件1> <文件2>` | 按共同字段连接文件 |
| `xargs` | 将 stdin 转换为命令行参数 |

---

## 四、压缩与归档

| 命令 | 说明 |
|------|------|
| `tar -czvf <归档.tar.gz> <目录>` | 创建 gzip 压缩归档 |
| `tar -xzvf <归档.tar.gz>` | 解压 tar.gz |
| `tar -cjvf <归档.tar.bz2> <目录>` | 创建 bzip2 压缩归档 |
| `tar -xjvf <归档.tar.bz2>` | 解压 tar.bz2 |
| `tar -xvf <归档.tar>` | 解压 tar（无压缩） |
| `tar -tf <归档>` | 查看归档内容 |
| `gzip <文件>` | 压缩文件（生成 .gz） |
| `gunzip <文件.gz>` | 解压 .gz |
| `bzip2 <文件>` | 压缩文件（生成 .bz2） |
| `bunzip2 <文件.bz2>` | 解压 .bz2 |
| `xz <文件>` | 压缩文件（生成 .xz） |
| `unxz <文件.xz>` | 解压 .xz |
| `zip -r <归档.zip> <目录>` | 创建 zip 压缩 |
| `unzip <归档.zip>` | 解压 zip |
| `rar a <归档.rar> <文件>` | 创建 rar 压缩（需安装 rar） |
| `unrar x <归档.rar>` | 解压 rar |
| `zcat <文件.gz>` | 查看 gz 压缩文件内容（不解压） |
| `zless <文件.gz>` | 分页查看 gz 压缩文件 |

---

## 五、进程管理

| 命令 | 说明 |
|------|------|
| `ps aux` | 查看所有进程详细信息 |
| `ps -ef` | 查看进程（标准格式） |
| `top` | 实时显示进程资源占用（按 q 退出） |
| `htop` | 增强版 top（需安装 htop） |
| `kill <PID>` | 终止进程 |
| `kill -9 <PID>` | 强制终止进程 |
| `killall <进程名>` | 按名称终止进程 |
| `pkill <进程名>` | 按名称模式终止进程 |
| `pgrep <进程名>` | 按名称查找进程 PID |
| `nice -n <优先级> <命令>` | 以指定优先级启动进程 |
| `renice <优先级> -p <PID>` | 调整运行中进程的优先级 |
| `nohup <命令> &` | 后台运行并忽略挂起信号 |
| `jobs` | 查看后台作业 |
| `fg %<作业号>` | 将后台作业调到前台 |
| `bg %<作业号>` | 将前台作业放到后台 |
| `disown %<作业号>` | 从 shell 中移除作业（关闭终端后仍运行） |
| `watch -n <秒> <命令>` | 每隔 N 秒执行一次命令 |
| `lsof -i :端口` | 查看占用端口的进程 |
| `strace -p <PID>` | 跟踪进程的系统调用 |
| `ltrace -p <PID>` | 跟踪进程的库调用 |

---

## 六、系统信息

| 命令 | 说明 |
|------|------|
| `uname -a` | 查看内核版本、架构等信息 |
| `hostnamectl` | 查看/设置主机名及相关信息 |
| `uptime` | 查看系统运行时间和负载 |
| `free -h` | 查看内存使用情况 |
| `vmstat 1` | 每秒显示虚拟内存、CPU 等统计 |
| `iostat -x 1` | 查看磁盘 I/O 统计 |
| `sar -u 1 3` | 查看 CPU 使用率（需安装 sysstat） |
| `dmesg \| tail -20` | 查看内核日志最后 20 行 |
| `lscpu` | 查看 CPU 架构信息 |
| `lsblk` | 查看块设备列表 |
| `blkid` | 查看块设备的 UUID 和文件系统类型 |
| `mount \| column -t` | 查看挂载点 |
| `dmidecode -t system` | 查看硬件信息（需 root） |
| `lsusb` | 查看 USB 设备 |
| `lspci` | 查看 PCI 设备 |
| `hwclock` | 查看硬件时钟 |
| `date` | 查看系统日期时间 |
| `cal` | 显示日历 |
| `timedatectl` | 查看/设置时区和时间同步状态 |

---

## 七、网络管理

| 命令 | 说明 |
|------|------|
| `ip addr` | 查看网络接口 IP 地址 |
| `ip link show` | 查看网络接口状态 |
| `ip route` | 查看路由表 |
| `ping <主机>` | 测试网络连通性 |
| `curl <URL>` | 发送 HTTP 请求 |
| `wget <URL>` | 下载文件 |
| `ss -tuln` | 查看监听端口（推荐替代 netstat） |
| `netstat -tulnp` | 查看监听端口（需安装 net-tools） |
| `traceroute <主机>` | 追踪路由路径 |
| `mtr <主机>` | 结合 ping 和 traceroute 的网络诊断工具 |
| `nslookup <域名>` | DNS 查询 |
| `dig <域名>` | 更详细的 DNS 查询 |
| `host <域名>` | 简单的 DNS 查询 |
| `nc -zv <主机> <端口>` | 测试端口是否开放 |
| `telnet <主机> <端口>` | 测试 TCP 连接 |
| `ssh <用户>@<主机>` | SSH 远程登录 |
| `scp <本地文件> <用户>@<主机>:<远程路径>` | 安全复制文件 |
| `rsync -avz <源> <目标>` | 增量同步文件 |
| `iftop` | 实时查看网络带宽使用（需安装 iftop） |
| `nethogs` | 按进程查看带宽使用 |
| `iptables -L -n` | 查看防火墙规则 |
| `ufw status` | 查看 UFW 防火墙状态 |
| `firewall-cmd --list-all` | 查看 firewalld 规则（CentOS/RHEL） |
| `nmcli dev status` | 查看 NetworkManager 管理的网络设备状态 |

---

## 八、包管理

### Debian/Ubuntu（apt）

| 命令 | 说明 |
|------|------|
| `apt update` | 更新软件包索引 |
| `apt upgrade -y` | 升级所有已安装包 |
| `apt install <包名>` | 安装软件包 |
| `apt remove <包名>` | 卸载软件包 |
| `apt purge <包名>` | 彻底卸载（含配置文件） |
| `apt autoremove` | 自动卸载不再需要的依赖 |
| `apt search <关键词>` | 搜索软件包 |
| `apt show <包名>` | 查看软件包信息 |
| `dpkg -l` | 列出所有已安装包 |
| `dpkg -i <deb文件>` | 安装本地 deb 包 |

### CentOS/RHEL/Fedora（dnf/yum）

| 命令 | 说明 |
|------|------|
| `dnf update` | 更新系统（yum update 等同） |
| `dnf install <包名>` | 安装软件包 |
| `dnf remove <包名>` | 卸载软件包 |
| `dnf search <关键词>` | 搜索软件包 |
| `dnf info <包名>` | 查看软件包信息 |
| `dnf list installed` | 列出已安装包 |
| `rpm -qa` | 列出所有已安装 rpm 包 |
| `rpm -ivh <rpm文件>` | 安装本地 rpm 包 |
| `rpm -e <包名>` | 卸载 rpm 包 |

### Arch Linux（pacman）

| 命令 | 说明 |
|------|------|
| `pacman -Syu` | 同步并更新系统 |
| `pacman -S <包名>` | 安装软件包 |
| `pacman -R <包名>` | 卸载软件包 |
| `pacman -Rs <包名>` | 卸载并删除依赖 |
| `pacman -Ss <关键词>` | 搜索软件包 |
| `pacman -Qi <包名>` | 查看已安装包信息 |

---

## 九、用户与组管理

| 命令 | 说明 |
|------|------|
| `whoami` | 显示当前用户名 |
| `id` | 显示当前用户 UID/GID 和所属组 |
| `users` | 显示当前登录的用户列表 |
| `who` | 显示当前登录用户及其登录信息 |
| `w` | 显示当前登录用户及其正在执行的命令 |
| `last` | 显示最近登录记录 |
| `lastb` | 显示失败登录记录 |
| `sudo <命令>` | 以超级用户权限执行命令 |
| `su - <用户名>` | 切换用户 |
| `passwd` | 修改当前用户密码 |
| `passwd <用户名>` | 修改指定用户密码（root） |
| `useradd -m <用户名>` | 创建用户并创建家目录 |
| `usermod -aG <组名> <用户名>` | 将用户添加到附加组 |
| `userdel -r <用户名>` | 删除用户并删除家目录 |
| `groupadd <组名>` | 创建组 |
| `groupdel <组名>` | 删除组 |
| `groups <用户名>` | 查看用户所属组 |
| `chage -l <用户名>` | 查看用户密码过期信息 |

---

## 十、磁盘与文件系统

| 命令 | 说明 |
|------|------|
| `fdisk -l` | 查看磁盘分区表 |
| `parted -l` | 查看分区信息（GPT 兼容） |
| `mkfs.ext4 /dev/sda1` | 格式化分区为 ext4 |
| `mkfs.xfs /dev/sda1` | 格式化分区为 XFS |
| `mount /dev/sda1 /mnt` | 挂载分区 |
| `umount /mnt` | 卸载分区 |
| `mount -a` | 挂载 /etc/fstab 中的所有文件系统 |
| `blkid` | 查看块设备的 UUID 和类型 |
| `lsblk -f` | 查看块设备及其文件系统 |
| `tune2fs -l /dev/sda1` | 查看 ext 文件系统详细信息 |
| `resize2fs /dev/sda1` | 调整 ext 文件系统大小 |
| `xfs_growfs /mount_point` | 扩展 XFS 文件系统 |
| `dd if=/dev/zero of=/tmp/test bs=1M count=100` | 创建指定大小的文件（用于测试） |
| `sync` | 将缓冲区数据写入磁盘 |
| `smartctl -a /dev/sda` | 查看硬盘 SMART 信息（需安装 smartmontools） |

---

## 十一、服务管理（systemd）

| 命令 | 说明 |
|------|------|
| `systemctl start <服务名>` | 启动服务 |
| `systemctl stop <服务名>` | 停止服务 |
| `systemctl restart <服务名>` | 重启服务 |
| `systemctl reload <服务名>` | 重新加载配置 |
| `systemctl enable <服务名>` | 设置开机自启 |
| `systemctl disable <服务名>` | 取消开机自启 |
| `systemctl status <服务名>` | 查看服务状态 |
| `systemctl is-active <服务名>` | 检查服务是否运行 |
| `systemctl list-units --type=service` | 列出所有服务单元 |
| `journalctl -u <服务名>` | 查看服务的日志 |
| `journalctl -f` | 实时跟踪系统日志 |
| `systemctl daemon-reload` | 重新加载 systemd 配置 |

---

## 十二、计划任务

| 命令 | 说明 |
|------|------|
| `crontab -l` | 查看当前用户的 crontab 任务 |
| `crontab -e` | 编辑当前用户的 crontab |
| `crontab -r` | 删除当前用户的 crontab |
| `at <时间>` | 在指定时间执行一次任务 |
| `atq` | 查看 at 任务队列 |
| `atrm <任务号>` | 删除 at 任务 |
| `systemctl list-timers` | 查看 systemd timer 任务 |

### crontab 格式示例

```
* * * * * /path/to/command       # 每分钟执行
*/5 * * * * /path/to/command     # 每5分钟
0 2 * * * /path/to/command       # 每天凌晨2点
0 0 1 * * /path/to/command       # 每月1日零点
0 9-17 * * 1-5 /path/to/command  # 工作日9点到17点每小时
```

---

## 十三、实用技巧

1. **历史命令**  
   ```bash
   history              # 查看历史
   !!                   # 执行上一条命令
   !$                   # 上一条命令的最后一个参数
   !字符串              # 执行最近以字符串开头的命令
   Ctrl + r             # 反向搜索历史
   ```

2. **快捷键**  
   ```
   Ctrl + a   # 光标移到行首
   Ctrl + e   # 光标移到行尾
   Ctrl + u   # 删除光标前所有字符
   Ctrl + k   # 删除光标后所有字符
   Ctrl + w   # 删除光标前一个单词
   Ctrl + y   # 粘贴刚才删除的内容
   Ctrl + l   # 清屏
   Ctrl + d   # 退出当前 shell
   Tab        # 自动补全
   ```

3. **重定向与管道**  
   ```bash
   command > file          # 标准输出重定向到文件（覆盖）
   command >> file         # 追加
   command 2>&1            # 将标准错误合并到标准输出
   command1 | command2     # 管道
   tee file                # 同时输出到文件和屏幕
   ```

4. **查找大文件**  
   ```bash
   find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null
   du -ah / | sort -rh | head -20
   ```

5. **批量重命名**  
   ```bash
   rename 's/旧/新/' *.txt           # Perl 版 rename
   for f in *.jpg; do mv "$f" "${f%.jpg}_new.jpg"; done  # Shell 循环
   ```

6. **后台运行并脱离终端**  
   ```bash
   nohup long-running-command &
   disown
   # 或使用 screen/tmux
   screen -S session_name
   tmux new -s session_name
   ```

7. **查看文件类型**  
   ```bash
   file filename
   ```

8. **生成随机密码**  
   ```bash
   openssl rand -base64 12
   date +%s | sha256sum | base64 | head -c 16
   ```

9. **查看命令帮助**  
   ```bash
   man command       # 手册页
   command --help    # 简要帮助
   info command      # info 文档
   whatis command    # 一句话描述
   ```

10. **安全删除文件（覆写）**  
    ```bash
    shred -u filename
    wipe filename       # 需安装 wipe
    ```

---

> **提示**：Linux 命令繁多，以上仅列出日常最常用的部分。如需深入了解某个命令，使用 `man <命令>` 查看完整手册。不同发行版的包管理器、服务管理工具可能有差异，请根据实际情况调整。