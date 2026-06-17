# Docker 常用命令速查手册

> 适用于 Docker Engine 20.10+，部分命令在旧版本可能略有差异。

---

## 一、镜像管理

| 命令 | 说明 |
|------|------|
| `docker images` | 列出本地所有镜像 |
| `docker search <名称>` | 从 Docker Hub 搜索镜像 |
| `docker pull <镜像名>:<标签>` | 拉取镜像（默认 latest） |
| `docker push <镜像名>:<标签>` | 推送镜像到仓库 |
| `docker rmi <镜像ID或名称>` | 删除本地镜像 |
| `docker image prune` | 清理未被使用的 dangling 镜像 |
| `docker tag <源镜像> <目标镜像>` | 给镜像打标签 |
| `docker save -o <文件.tar> <镜像名>` | 导出镜像为 tar 文件 |
| `docker load -i <文件.tar>` | 从 tar 文件导入镜像 |
| `docker history <镜像名>` | 查看镜像构建历史 |

---

## 二、容器生命周期

| 命令 | 说明 |
|------|------|
| `docker run <选项> <镜像> [命令]` | 创建并启动一个新容器 |
| `docker start <容器ID或名称>` | 启动已停止的容器 |
| `docker stop <容器ID或名称>` | 停止运行中的容器 |
| `docker restart <容器ID或名称>` | 重启容器 |
| `docker pause <容器ID>` | 暂停容器内所有进程 |
| `docker unpause <容器ID>` | 恢复暂停的容器 |
| `docker kill <容器ID>` | 强制终止容器 |
| `docker rm <容器ID或名称>` | 删除已停止的容器 |
| `docker container prune` | 删除所有已停止的容器 |
| `docker create <选项> <镜像>` | 只创建容器但不启动 |

### 常用 `docker run` 选项

| 选项 | 作用 |
|------|------|
| `-d` | 后台运行（detach） |
| `--name <名称>` | 指定容器名称 |
| `-p 宿主机端口:容器端口` | 端口映射 |
| `-v 宿主机路径:容器路径` | 挂载卷 |
| `-e KEY=VALUE` | 设置环境变量 |
| `--restart always` | 设置自动重启策略 |
| `--network <网络名>` | 指定网络 |
| `-it` | 交互式终端（常用于进入容器） |
| `--rm` | 容器停止后自动删除 |

---

## 三、容器操作与信息

| 命令 | 说明 |
|------|------|
| `docker ps` | 列出运行中的容器 |
| `docker ps -a` | 列出所有容器（包括已停止） |
| `docker logs <容器ID>` | 查看容器日志 |
| `docker logs -f <容器ID>` | 实时跟踪日志 |
| `docker exec -it <容器ID> bash` | 进入容器内部（交互式） |
| `docker cp <容器ID>:<路径> <宿主机路径>` | 从容器复制文件到宿主机 |
| `docker cp <宿主机路径> <容器ID>:<路径>` | 从宿主机复制文件到容器 |
| `docker top <容器ID>` | 查看容器内的进程 |
| `docker stats` | 实时显示容器资源使用情况 |
| `docker inspect <容器ID>` | 查看容器的详细信息（JSON） |
| `docker port <容器ID>` | 查看端口映射情况 |
| `docker diff <容器ID>` | 查看容器文件系统的变化 |

---

## 四、网络管理

| 命令 | 说明 |
|------|------|
| `docker network ls` | 列出所有网络 |
| `docker network create <网络名>` | 创建自定义网络 |
| `docker network connect <网络名> <容器>` | 将容器连接到网络 |
| `docker network disconnect <网络名> <容器>` | 断开容器与网络的连接 |
| `docker network inspect <网络名>` | 查看网络详情 |
| `docker network prune` | 删除未使用的网络 |

---

## 五、数据卷管理

| 命令 | 说明 |
|------|------|
| `docker volume ls` | 列出所有卷 |
| `docker volume create <卷名>` | 创建一个卷 |
| `docker volume inspect <卷名>` | 查看卷详情 |
| `docker volume rm <卷名>` | 删除卷 |
| `docker volume prune` | 删除所有未使用的卷 |

---

## 六、Docker Compose

| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 启动所有服务（后台） |
| `docker-compose down` | 停止并移除容器、网络等 |
| `docker-compose logs -f` | 查看所有服务的日志 |
| `docker-compose ps` | 列出服务状态 |
| `docker-compose exec <服务名> bash` | 进入某个服务的容器 |
| `docker-compose build` | 重新构建镜像 |
| `docker-compose pull` | 拉取服务所需的镜像 |
| `docker-compose restart` | 重启所有服务 |
| `docker-compose config` | 验证并查看最终的 compose 配置 |

---

## 七、构建镜像

| 命令 | 说明 |
|------|------|
| `docker build -t <镜像名>:<标签> .` | 根据 Dockerfile 构建镜像 |
| `docker build --no-cache -t <镜像名> .` | 不使用缓存构建 |
| `docker commit <容器ID> <新镜像名>` | 将容器保存为新镜像（不推荐） |
| `docker export -o <文件.tar> <容器ID>` | 导出容器快照 |
| `docker import <文件.tar> <镜像名>` | 导入快照为镜像 |

---

## 八、系统信息与管理

| 命令 | 说明 |
|------|------|
| `docker version` | 显示 Docker 版本信息 |
| `docker info` | 显示系统信息（内核、存储驱动等） |
| `docker system df` | 查看磁盘使用情况 |
| `docker system prune -a` | 清理所有未使用的资源（镜像、容器、网络、卷） |
| `docker login` | 登录 Docker Hub 或私有仓库 |
| `docker logout` | 登出 |
| `docker events` | 实时获取 Docker 事件流 |

---

## 九、实用技巧

1. **一键进入容器**  
   ```bash
   docker exec -it $(docker ps -q) bash
   ```

2. **删除所有容器**  
   ```bash
   docker rm -f $(docker ps -aq)
   ```

3. **删除所有镜像**  
   ```bash
   docker rmi -f $(docker images -q)
   ```

4. **查看容器 IP 地址**  
   ```bash
   docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <容器ID>
   ```

5. **限制容器资源**  
   ```bash
   docker run --memory="512m" --cpus="1.5" ...
   ```

---

> **提示**：如需详细帮助，可使用 `docker <子命令> --help` 查看。