# MySQL 常用命令速查手册

> 适用版本：MySQL 5.7+ / 8.0+，部分命令在 MariaDB 中可能略有差异。

---

## 一、连接与退出

| 命令 | 说明 |
|------|------|
| `mysql -u root -p` | 连接 MySQL（回车后输入密码） |
| `mysql -h 主机 -P 端口 -u 用户名 -p` | 指定主机和端口连接 |
| `exit` 或 `quit` | 退出 MySQL 客户端 |
| `\q` | 退出（简写） |
| `status;` | 查看当前连接状态 |
| `SELECT VERSION();` | 查看 MySQL 版本 |

---

## 二、数据库操作（DDL）

| 命令 | 说明 |
|------|------|
| `SHOW DATABASES;` | 列出所有数据库 |
| `CREATE DATABASE <库名> DEFAULT CHARSET utf8mb4;` | 创建数据库（指定字符集） |
| `USE <库名>;` | 切换到指定数据库 |
| `SELECT DATABASE();` | 查看当前所在数据库 |
| `DROP DATABASE <库名>;` | 删除数据库 |
| `ALTER DATABASE <库名> CHARACTER SET utf8mb4;` | 修改数据库字符集 |

---

## 三、表操作（DDL）

| 命令 | 说明 |
|------|------|
| `SHOW TABLES;` | 列出当前库的所有表 |
| `DESC <表名>;` | 查看表结构 |
| `SHOW CREATE TABLE <表名>;` | 查看建表语句 |
| `CREATE TABLE <表名> (列定义);` | 创建表 |
| `DROP TABLE <表名>;` | 删除表 |
| `TRUNCATE TABLE <表名>;` | 清空表数据（重置自增ID） |
| `ALTER TABLE <表名> ADD COLUMN <列名> 类型;` | 添加列 |
| `ALTER TABLE <表名> DROP COLUMN <列名>;` | 删除列 |
| `ALTER TABLE <表名> MODIFY COLUMN <列名> 新类型;` | 修改列类型 |
| `ALTER TABLE <表名> CHANGE <旧列名> <新列名> 类型;` | 重命名列 |
| `ALTER TABLE <表名> RENAME TO <新表名>;` | 重命名表 |
| `ALTER TABLE <表名> ADD INDEX <索引名>(列);` | 添加索引 |
| `ALTER TABLE <表名> DROP INDEX <索引名>;` | 删除索引 |
| `SHOW INDEX FROM <表名>;` | 查看表的索引 |

---

## 四、数据操作（DML）

| 命令 | 说明 |
|------|------|
| `INSERT INTO <表名> VALUES (...);` | 插入一行（全部字段） |
| `INSERT INTO <表名>(列1,列2) VALUES (值1,值2);` | 插入指定字段 |
| `INSERT INTO <表名> VALUES (...),(...);` | 批量插入 |
| `UPDATE <表名> SET 列=值 WHERE 条件;` | 更新数据（**务必加WHERE**） |
| `DELETE FROM <表名> WHERE 条件;` | 删除数据（**务必加WHERE**） |
| `REPLACE INTO <表名> VALUES (...);` | 插入或替换（主键/唯一键冲突时先删后插） |

---

## 五、数据查询（DQL）

| 命令 | 说明 |
|------|------|
| `SELECT * FROM <表名>;` | 查询所有列 |
| `SELECT 列1,列2 FROM <表名>;` | 查询指定列 |
| `SELECT DISTINCT 列 FROM <表名>;` | 去重查询 |
| `SELECT * FROM <表名> WHERE 条件;` | 条件查询 |
| `SELECT * FROM <表名> ORDER BY 列 ASC/DESC;` | 排序 |
| `SELECT * FROM <表名> LIMIT 偏移量, 行数;` | 分页查询 |
| `SELECT COUNT(*) FROM <表名>;` | 统计行数 |
| `SELECT AVG(列), SUM(列), MAX(列), MIN(列) FROM <表名>;` | 聚合函数 |
| `SELECT 列, COUNT(*) FROM <表名> GROUP BY 列;` | 分组统计 |
| `SELECT ... HAVING 条件;` | 分组后筛选 |
| `SELECT * FROM A JOIN B ON A.id = B.a_id;` | 内连接 |
| `SELECT * FROM A LEFT JOIN B ON A.id = B.a_id;` | 左外连接 |
| `SELECT * FROM A RIGHT JOIN B ON A.id = B.a_id;` | 右外连接 |
| `SELECT * FROM A WHERE id IN (SELECT id FROM B);` | 子查询 |
| `SELECT * FROM A WHERE EXISTS (SELECT 1 FROM B WHERE ...);` | EXISTS 子查询 |
| `SELECT * FROM <表名> WHERE 列 LIKE '%关键词%';` | 模糊查询 |
| `SELECT * FROM <表名> WHERE 列 BETWEEN a AND b;` | 范围查询 |
| `SELECT * FROM <表名> WHERE 列 IS NULL;` | 判空查询 |

---

## 六、用户与权限管理（DCL）

| 命令 | 说明 |
|------|------|
| `CREATE USER '用户名'@'主机' IDENTIFIED BY '密码';` | 创建用户 |
| `DROP USER '用户名'@'主机';` | 删除用户 |
| `ALTER USER '用户名'@'主机' IDENTIFIED BY '新密码';` | 修改密码 |
| `GRANT 权限 ON 库.表 TO '用户名'@'主机';` | 授予权限 |
| `REVOKE 权限 ON 库.表 FROM '用户名'@'主机';` | 撤销权限 |
| `FLUSH PRIVILEGES;` | 刷新权限 |
| `SHOW GRANTS FOR '用户名'@'主机';` | 查看用户权限 |
| `SELECT user, host FROM mysql.user;` | 查看所有用户 |

### 常用权限示例

```sql
-- 授予所有权限（类似root）
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 授予对特定库的所有权限
GRANT ALL PRIVILEGES ON mydb.* TO 'app_user'@'192.168.%';

-- 授予只读权限
GRANT SELECT ON mydb.* TO 'readonly'@'%';
```

---

## 七、事务控制

| 命令 | 说明 |
|------|------|
| `START TRANSACTION;` | 开启事务 |
| `COMMIT;` | 提交事务 |
| `ROLLBACK;` | 回滚事务 |
| `SAVEPOINT <保存点名>;` | 设置保存点 |
| `ROLLBACK TO <保存点名>;` | 回滚到保存点 |
| `SET AUTOCOMMIT = 0;` | 关闭自动提交（当前会话） |

---

## 八、备份与恢复

| 命令 | 说明 |
|------|------|
| `mysqldump -u root -p <库名> > backup.sql` | 备份单个数据库 |
| `mysqldump -u root -p --all-databases > all.sql` | 备份所有数据库 |
| `mysqldump -u root -p <库名> <表名> > table.sql` | 备份单张表 |
| `mysql -u root -p <库名> < backup.sql` | 恢复数据库 |
| `mysql -u root -p < backup.sql` | 恢复整个备份（包含建库语句） |
| `source /path/to/backup.sql;` | 在 MySQL 客户端内执行 SQL 文件 |

### mysqldump 常用选项

| 选项 | 作用 |
|------|------|
| `--single-transaction` | InnoDB 热备份（不加锁） |
| `--routines` | 包含存储过程和函数 |
| `--triggers` | 包含触发器 |
| `--events` | 包含事件 |
| `--add-drop-table` | 在 CREATE 前加 DROP TABLE |
| `--compress` | 压缩传输 |
| `--where="条件"` | 只导出满足条件的行 |

---

## 九、性能与状态查看

| 命令 | 说明 |
|------|------|
| `SHOW PROCESSLIST;` | 查看当前连接线程 |
| `KILL <线程ID>;` | 杀死指定线程 |
| `EXPLAIN SELECT ...;` | 查看查询执行计划 |
| `SHOW VARIABLES LIKE '%xxx%';` | 查看系统变量 |
| `SHOW STATUS LIKE '%xxx%';` | 查看状态变量 |
| `SHOW ENGINE INNODB STATUS\G` | 查看 InnoDB 引擎状态 |
| `SELECT @@tx_isolation;` (8.0: `@@transaction_isolation`) | 查看事务隔离级别 |
| `SET GLOBAL slow_query_log = ON;` | 开启慢查询日志 |

---

## 十、实用技巧

1. **查看建表语句（含字符集、引擎）**  
   ```sql
   SHOW CREATE TABLE 表名\G
   ```

2. **复制表结构**  
   ```sql
   CREATE TABLE 新表 LIKE 旧表;
   ```

3. **复制表数据**  
   ```sql
   INSERT INTO 新表 SELECT * FROM 旧表;
   ```

4. **修改表引擎**  
   ```sql
   ALTER TABLE 表名 ENGINE = InnoDB;
   ```

5. **查看表大小**  
   ```sql
   SELECT table_schema, table_name, 
          ROUND((data_length+index_length)/1024/1024,2) AS size_MB 
   FROM information_schema.tables 
   WHERE table_schema = '库名';
   ```

6. **清屏**（MySQL 客户端内）  
   ```
   system clear;   -- Linux
   system cls;     -- Windows
   ```

7. **使用 pager 分页查看结果**  
   ```sql
   pager less -S;   -- 水平滚动查看宽表
   nopager;         -- 取消 pager
   ```

8. **安全更新模式**（防止误 UPDATE/DELETE 不带 WHERE）  
   ```sql
   SET SQL_SAFE_UPDATES = 1;
   ```

---

> **提示**：MySQL 8.0 中部分变量名有所变更（如 `tx_isolation` → `transaction_isolation`），遇到报错时可查阅官方文档。如需帮助，可在 MySQL 客户端内使用 `HELP 关键字;` 查看语法。