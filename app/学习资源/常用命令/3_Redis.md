# Redis 常用命令速查手册

> 适用版本：Redis 6.x / 7.x，部分命令在高版本中有扩展（如 `WAITAOF`）。

---

## 一、连接与服务器管理

| 命令 | 说明 |
|------|------|
| `redis-cli` | 启动命令行客户端（默认 127.0.0.1:6379） |
| `redis-cli -h 主机 -p 端口 -a 密码` | 远程连接 |
| `AUTH 密码` | 认证（若配置了 requirepass） |
| `PING` | 测试连通性（返回 PONG） |
| `ECHO 消息` | 打印消息 |
| `QUIT` | 断开连接 |
| `SELECT 库编号` | 切换数据库（0-15，默认16个） |
| `INFO` | 查看服务器信息（内存、CPU、持久化等） |
| `INFO 段名` | 查看特定段，如 `INFO memory`, `INFO replication` |
| `CONFIG GET 参数名` | 获取配置参数值 |
| `CONFIG SET 参数名 值` | 动态修改配置（重启失效） |
| `CONFIG REWRITE` | 将当前配置写入 redis.conf |
| `DBSIZE` | 返回当前数据库的 key 数量 |
| `FLUSHDB` | 清空当前数据库 |
| `FLUSHALL` | 清空所有数据库 |
| `CLIENT LIST` | 查看所有客户端连接 |
| `CLIENT KILL ip:port` | 杀死指定客户端 |
| `MONITOR` | 实时监控所有命令（调试用，慎用） |
| `SLOWLOG GET N` | 获取最近 N 条慢查询 |
| `TIME` | 返回 Redis 服务器时间戳 |

---

## 二、键（Key）操作

| 命令 | 说明 |
|------|------|
| `KEYS pattern` | 查找所有匹配模式的 key（**生产慎用**，可用 SCAN） |
| `SCAN cursor [MATCH pattern] [COUNT count]` | 增量迭代 key（推荐代替 KEYS） |
| `EXISTS key` | 判断 key 是否存在 |
| `TYPE key` | 返回 key 的类型 |
| `DEL key [key ...]` | 删除一个或多个 key |
| `UNLINK key [key ...]` | 异步删除（非阻塞，推荐替代 DEL） |
| `RENAME key newkey` | 重命名 key |
| `RENAMENX key newkey` | 仅当 newkey 不存在时重命名 |
| `EXPIRE key seconds` | 设置过期时间（秒） |
| `PEXPIRE key milliseconds` | 设置过期时间（毫秒） |
| `TTL key` | 查看剩余生存时间（秒，-1 永不过期，-2 已过期） |
| `PTTL key` | 查看剩余生存时间（毫秒） |
| `PERSIST key` | 移除过期时间，使 key 永不过期 |
| `RANDOMKEY` | 随机返回一个 key |
| `DUMP key` | 序列化 key 的值 |
| `RESTORE key ttl serialized-value` | 反序列化恢复 key |
| `OBJECT ENCODING key` | 查看 key 的内部编码方式 |
| `OBJECT IDLETIME key` | 查看 key 的空闲时间 |

---

## 三、字符串（String）

| 命令 | 说明 |
|------|------|
| `SET key value [NX\|XX] [EX sec] [PX ms]` | 设置值（NX 不存在时设，XX 存在时设） |
| `GET key` | 获取值 |
| `GETSET key value` | 设置新值并返回旧值 |
| `MSET key value [key value ...]` | 批量设置 |
| `MGET key [key ...]` | 批量获取 |
| `STRLEN key` | 获取值的长度 |
| `APPEND key value` | 追加字符串 |
| `INCR key` | 自增 1 |
| `INCRBY key increment` | 增加指定整数 |
| `INCRBYFLOAT key increment` | 增加指定浮点数 |
| `DECR key` | 自减 1 |
| `DECRBY key decrement` | 减少指定整数 |
| `SETRANGE key offset value` | 从偏移量开始覆盖 |
| `GETRANGE key start end` | 获取子串（包含 start 和 end） |
| `SETEX key seconds value` | 设置值并同时设置过期时间（秒） |
| `PSETEX key milliseconds value` | 设置值并同时设置过期时间（毫秒） |
| `SETNX key value` | 仅当 key 不存在时设置（分布式锁基础） |

---

## 四、哈希（Hash）

| 命令 | 说明 |
|------|------|
| `HSET key field value [field value ...]` | 设置一个或多个字段 |
| `HGET key field` | 获取字段值 |
| `HMGET key field [field ...]` | 获取多个字段值 |
| `HGETALL key` | 获取所有字段和值 |
| `HKEYS key` | 获取所有字段名 |
| `HVALS key` | 获取所有字段值 |
| `HLEN key` | 获取字段数量 |
| `HEXISTS key field` | 判断字段是否存在 |
| `HDEL key field [field ...]` | 删除一个或多个字段 |
| `HINCRBY key field increment` | 对字段值自增整数 |
| `HINCRBYFLOAT key field increment` | 对字段值自增浮点数 |
| `HSETNX key field value` | 仅当字段不存在时设置 |
| `HSTRLEN key field` | 获取字段值的长度 |
| `HRANDFIELD key [count]` | 随机返回字段（可指定个数） |

---

## 五、列表（List）

| 命令 | 说明 |
|------|------|
| `LPUSH key value [value ...]` | 从左侧推入元素 |
| `RPUSH key value [value ...]` | 从右侧推入元素 |
| `LPOP key [count]` | 从左侧弹出元素 |
| `RPOP key [count]` | 从右侧弹出元素 |
| `BLPOP key [key ...] timeout` | 阻塞式左侧弹出 |
| `BRPOP key [key ...] timeout` | 阻塞式右侧弹出 |
| `LLEN key` | 获取列表长度 |
| `LRANGE key start stop` | 获取指定范围的元素（0 起始，-1 表示最后一个） |
| `LINDEX key index` | 获取指定索引的元素 |
| `LSET key index value` | 设置指定索引的元素值 |
| `LINSERT key BEFORE\|AFTER pivot value` | 在基准元素前/后插入 |
| `LREM key count value` | 删除等于 value 的元素（count>0 从左删，<0 从右删，=0 删全部） |
| `LTRIM key start stop` | 截取列表，只保留指定范围 |
| `RPOPLPUSH source destination` | 从 source 右侧弹出并推入 destination 左侧 |
| `BRPOPLPUSH source destination timeout` | 阻塞式 RPOPLPUSH |
| `LMOVE source destination LEFT\|RIGHT LEFT\|RIGHT` | 原子性移动元素（Redis 6.2+） |
| `BLMOVE ...` | 阻塞版 LMOVE |

---

## 六、集合（Set）

| 命令 | 说明 |
|------|------|
| `SADD key member [member ...]` | 添加一个或多个成员 |
| `SREM key member [member ...]` | 移除一个或多个成员 |
| `SMEMBERS key` | 获取所有成员 |
| `SCARD key` | 获取成员数量 |
| `SISMEMBER key member` | 判断是否是成员 |
| `SRANDMEMBER key [count]` | 随机返回一个或多个成员（不删除） |
| `SPOP key [count]` | 随机移除并返回一个或多个成员 |
| `SMOVE source destination member` | 将成员从一个集合移动到另一个 |
| `SINTER key [key ...]` | 交集 |
| `SINTERSTORE destination key [key ...]` | 交集并存入新集合 |
| `SUNION key [key ...]` | 并集 |
| `SUNIONSTORE destination key [key ...]` | 并集并存入新集合 |
| `SDIFF key [key ...]` | 差集 |
| `SDIFFSTORE destination key [key ...]` | 差集并存入新集合 |
| `SSCAN key cursor [MATCH pattern] [COUNT count]` | 增量迭代集合成员 |

---

## 七、有序集合（Sorted Set）

| 命令 | 说明 |
|------|------|
| `ZADD key score member [score member ...]` | 添加一个或多个成员（分数可为整数或浮点数） |
| `ZREM key member [member ...]` | 移除一个或多个成员 |
| `ZCARD key` | 获取成员数量 |
| `ZCOUNT key min max` | 统计分数在 min~max 之间的成员数 |
| `ZSCORE key member` | 获取成员的分数 |
| `ZINCRBY key increment member` | 增加成员的分数 |
| `ZRANK key member` | 获取成员排名（从小到大，0 起始） |
| `ZREVRANK key member` | 获取成员排名（从大到小） |
| `ZRANGE key start stop [WITHSCORES]` | 按排名范围获取成员（从小到大） |
| `ZREVRANGE key start stop [WITHSCORES]` | 按排名范围获取成员（从大到小） |
| `ZRANGEBYSCORE key min max [WITHSCORES] [LIMIT offset count]` | 按分数范围获取成员 |
| `ZREVRANGEBYSCORE key max min [WITHSCORES] [LIMIT offset count]` | 按分数范围倒序获取 |
| `ZRANK key member` | 获取排名（升序） |
| `ZREVRANK key member` | 获取排名（降序） |
| `ZREM key member [member ...]` | 移除成员 |
| `ZREMRANGEBYRANK key start stop` | 移除指定排名范围内的成员 |
| `ZREMRANGEBYSCORE key min max` | 移除指定分数范围内的成员 |
| `ZINTERSTORE destination numkeys key [key ...] [WEIGHTS w] [AGGREGATE SUM\|MIN\|MAX]` | 交集运算 |
| `ZUNIONSTORE destination numkeys key [key ...] [WEIGHTS w] [AGGREGATE SUM\|MIN\|MAX]` | 并集运算 |
| `ZSCAN key cursor [MATCH pattern] [COUNT count]` | 增量迭代有序集合 |

---

## 八、HyperLogLog

| 命令 | 说明 |
|------|------|
| `PFADD key element [element ...]` | 添加元素 |
| `PFCOUNT key [key ...]` | 返回基数估算值（误差约 0.81%） |
| `PFMERGE destkey sourcekey [sourcekey ...]` | 合并多个 HyperLogLog |

---

## 九、位图（Bitmap）

| 命令 | 说明 |
|------|------|
| `SETBIT key offset value` | 设置指定偏移位的值（0 或 1） |
| `GETBIT key offset` | 获取指定偏移位的值 |
| `BITCOUNT key [start end]` | 统计值为 1 的位数 |
| `BITPOS key bit [start [end]]` | 查找第一个值为 0 或 1 的位 |
| `BITOP operation destkey key [key ...]` | 位运算（AND/OR/XOR/NOT） |
| `BITFIELD key [GET type offset] [SET type offset value] ...` | 位域操作（支持多类型） |

---

## 十、地理空间（Geo）

| 命令 | 说明 |
|------|------|
| `GEOADD key longitude latitude member [longitude latitude member ...]` | 添加地理位置 |
| `GEOPOS key member [member ...]` | 获取位置的经纬度 |
| `GEODIST key member1 member2 [unit]` | 计算两地距离（m/km/mi/ft） |
| `GEORADIUS key longitude latitude radius unit [WITHCOORD] [WITHDIST] [COUNT count]` | 查询半径内的成员 |
| `GEORADIUSBYMEMBER key member radius unit ...` | 以成员为中心查询 |
| `GEOSEARCH key FROMMEMBER member BYRADIUS radius unit ...` | 更灵活的搜索（Redis 6.2+） |
| `GEOSEARCHSTORE destination source ...` | 搜索结果存入新 key |

---

## 十一、流（Stream）

| 命令 | 说明 |
|------|------|
| `XADD key [NOMKSTREAM] [MAXLEN [~] count] * field value [field value ...]` | 添加消息 |
| `XLEN key` | 获取消息长度 |
| `XRANGE key start end [COUNT count]` | 按 ID 范围获取消息 |
| `XREVRANGE key end start [COUNT count]` | 倒序获取消息 |
| `XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] ID [ID ...]` | 读取消息（支持阻塞） |
| `XGROUP CREATE key groupname id-or-$ [MKSTREAM]` | 创建消费者组 |
| `XREADGROUP GROUP group consumer [COUNT count] [BLOCK ms] STREAMS key [key ...] ID [ID ...]` | 消费者组读取 |
| `XACK key group ID [ID ...]` | 确认消息已被处理 |
| `XPENDING key group [start end count] [consumer]` | 查看待处理消息 |
| `XCLAIM key group consumer min-idle-time ID [ID ...]` | 转移消息所有权 |
| `XDEL key ID [ID ...]` | 删除消息 |
| `XTRIM key MAXLEN [~] count` | 裁剪流到指定长度 |

---

## 十二、发布/订阅

| 命令 | 说明 |
|------|------|
| `PUBLISH channel message` | 向频道发布消息 |
| `SUBSCRIBE channel [channel ...]` | 订阅一个或多个频道 |
| `UNSUBSCRIBE [channel ...]` | 退订频道 |
| `PSUBSCRIBE pattern [pattern ...]` | 订阅模式匹配的频道 |
| `PUNSUBSCRIBE [pattern ...]` | 退订模式匹配的频道 |
| `PUBSUB CHANNELS [pattern]` | 查看活跃频道 |
| `PUBSUB NUMSUB channel [channel ...]` | 查看频道订阅数 |
| `PUBSUB NUMPAT` | 查看模式订阅数 |

---

## 十三、事务

| 命令 | 说明 |
|------|------|
| `MULTI` | 开启事务 |
| `EXEC` | 执行事务 |
| `DISCARD` | 放弃事务 |
| `WATCH key [key ...]` | 监视 key（乐观锁，配合 MULTI 使用） |
| `UNWATCH` | 取消监视 |

### 事务示例

```redis
WATCH stock:item001
val = GET stock:item001
if val > 0 then
    MULTI
    DECR stock:item001
    EXEC
else
    UNWATCH
end
```

---

## 十四、Lua 脚本

| 命令 | 说明 |
|------|------|
| `EVAL script numkeys key [key ...] arg [arg ...]` | 执行 Lua 脚本 |
| `EVALSHA sha1 numkeys key [key ...] arg [arg ...]` | 执行已缓存的脚本 |
| `SCRIPT LOAD script` | 将脚本加载到缓存，返回 SHA |
| `SCRIPT EXISTS sha1 [sha1 ...]` | 检查脚本是否缓存 |
| `SCRIPT FLUSH` | 清空脚本缓存 |
| `SCRIPT KILL` | 杀死正在执行的脚本 |

---

## 十五、持久化与备份

| 命令 | 说明 |
|------|------|
| `SAVE` | 同步保存 RDB 快照（阻塞） |
| `BGSAVE` | 后台异步保存 RDB 快照 |
| `LASTSAVE` | 查看最后一次成功保存的时间戳 |
| `BGREWRITEAOF` | 后台重写 AOF 文件 |
| `SHUTDOWN [NOSAVE\|SAVE]` | 关闭服务器（可选是否保存） |
| `DEBUG RELOAD` | 重新加载数据（开发用） |
| `SWAPDB db1 db2` | 交换两个数据库的数据 |

---

## 十六、集群管理

| 命令 | 说明 |
|------|------|
| `CLUSTER INFO` | 查看集群状态 |
| `CLUSTER NODES` | 查看集群节点信息 |
| `CLUSTER MEET ip port` | 将节点加入集群 |
| `CLUSTER FORGET node-id` | 从集群中移除节点 |
| `CLUSTER REPLICATE node-id` | 设置当前节点为指定节点的副本 |
| `CLUSTER FAILOVER [FORCE\|TAKEOVER]` | 手动故障转移 |
| `CLUSTER ADDSLOTS slot [slot ...]` | 分配槽位 |
| `CLUSTER DELSLOTS slot [slot ...]` | 移除槽位 |
| `CLUSTER FLUSHSLOTS` | 清空所有槽位 |
| `CLUSTER KEYSLOT key` | 计算 key 所在的槽位 |
| `CLUSTER COUNTKEYSINSLOT slot` | 查看槽位中的 key 数量 |
| `CLUSTER GETKEYSINSLOT slot count` | 返回槽位中的 key |
| `CLUSTER RESET [HARD\|SOFT]` | 重置集群节点 |
| `CLUSTER BUMPEPOCH` | 推进纪元（节点分裂时使用） |
| `READONLY` / `READWRITE` | 在从节点上切换读写模式 |

---

## 十七、性能诊断与监控

| 命令 | 说明 |
|------|------|
| `INFO COMMANDSTATS` | 查看命令调用次数和耗时 |
| `MEMORY USAGE key [SAMPLES count]` | 估算 key 的内存占用 |
| `MEMORY STATS` | 查看内存统计 |
| `MEMORY PURGE` | 尝试释放内存（仅限 jemalloc） |
| `MEMORY DOCTOR` | 内存健康诊断 |
| `LATENCY LATEST` | 查看最新延迟样本 |
| `LATENCY HISTORY event` | 查看延迟历史 |
| `LATENCY GRAPH event` | ASCII 延迟图 |
| `LATENCY DOCTOR` | 延迟健康诊断 |
| `ACL WHOAMI` | 查看当前用户（Redis 6+ ACL） |
| `ACL LIST` | 列出所有用户及其权限 |
| `ACL SETUSER username [rules]` | 创建/修改用户 |
| `ACL DELUSER username` | 删除用户 |
| `ACL LOG [count]` | 查看 ACL 拒绝日志 |

---

## 十八、实用技巧

1. **清空当前数据库所有 key**  
   ```redis
   FLUSHDB ASYNC
   ```

2. **设置 key 同时带过期时间**  
   ```redis
   SET token:abc123 "user_info" EX 3600 NX
   ```

3. **分布式锁（Redlock 简易版）**  
   ```redis
   SET lock:resource1 "uuid-xxx" NX EX 10
   -- 执行业务...
   DEL lock:resource1
   ```

4. **限流（滑动窗口计数器）**  
   ```redis
   INCR rate_limit:user:123
   EXPIRE rate_limit:user:123 60
   ```

5. **排行榜（有序集合）**  
   ```redis
   ZADD leaderboard 100 "player1"
   ZREVRANGE leaderboard 0 9 WITHSCORES   -- 前十名
   ```

6. **消息队列（List 实现）**  
   ```redis
   LPUSH queue:task "job1"
   BRPOP queue:task 0   -- 消费者阻塞等待
   ```

7. **布隆过滤器（Redis Stack / RediSearch 模块）**  
   ```redis
   BF.ADD bloom:urls "https://example.com"
   BF.EXISTS bloom:urls "https://example.com"
   ```

8. **慢查询定位**  
   ```redis
   CONFIG SET slowlog-log-slower-than 10000   -- 设置阈值（微秒）
   SLOWLOG GET 5
   ```

9. **大 key 扫描（推荐使用 redis-cli）**  
   ```bash
   redis-cli --bigkeys
   ```

10. **批量删除匹配的 key**  
    ```bash
    redis-cli KEYS "prefix:*" | xargs redis-cli DEL
    # 或使用 SCAN 安全版
    redis-cli --scan --pattern "prefix:*" | xargs redis-cli UNLINK
    ```

---

> **提示**：Redis 7.0 新增了 `FUNCTION` 命令族（支持 JavaScript 引擎），`ACL` 增强，`SHUTDOWN` 支持 `NOW` 选项等。详细帮助可在 redis-cli 中使用 `HELP 命令名` 查看。