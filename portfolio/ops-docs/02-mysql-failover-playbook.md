# MySQL 主从切换故障处理 Playbook

## 适用场景

MySQL 主从架构中主库故障，需要执行主从切换以恢复服务。

## 前置条件

- 主从架构已部署（至少 1 主 1 从）
- 已配置 MHA / Orchestrator 或手动切换流程
- 应用层已配置读写分离连接池

## 切换决策树

```
主库不可用
├── 从库延迟 < 3 秒？
│   ├── 是 → 执行标准切换（提升从库为新主）
│   └── 否 → 等待从库追平 OR 有损切换（丢数据风险）
├── 主库可恢复（网络抖动 / 进程重启）？
│   ├── 预计恢复 < 5 分钟 → 等待恢复，不切换
│   └── 预计恢复 > 5 分钟 → 执行切换
└── 核心业务影响？
    ├── 是 → 立即切换，不等从库追平
    └── 否 → 等待从库延迟 < 3 秒后切换
```

## 标准切换步骤（手动）

### 1. 确认主库状态

```bash
# 检查主库是否真的不可用
mysql -h <master-host> -u <user> -p -e "SELECT 1;"
# 检查主库进程
systemctl status mysqld
# 检查端口
telnet <master-host> 3306
```

### 2. 检查从库状态

```bash
# 登录从库
mysql -h <slave-host> -u <user> -p

# 查看复制状态
SHOW SLAVE STATUS\G
# 关注：
# - Slave_IO_Running: Yes
# - Slave_SQL_Running: Yes
# - Seconds_Behind_Master: 越小越好

# 确认从库数据完整性
SHOW MASTER STATUS;
```

### 3. 提升从库为新主库

```bash
# 登录从库
mysql -h <slave-host> -u <user> -p

# 停止复制
STOP SLAVE;
RESET SLAVE ALL;

# 开启读写
SET GLOBAL read_only = OFF;
SET GLOBAL super_read_only = OFF;

# 记录新的 binlog 位点
SHOW MASTER STATUS;
```

### 4. 更新应用连接配置

- 修改数据库连接配置，指向新主库
- 通过配置中心（如 Nacos/Consul）热更新，避免重启
- 确认写入流量切换到新主库

### 5. 旧主库恢复后处理

```bash
# 旧主库恢复后，作为从库重新加入
# 登录旧主库
mysql -u <user> -p

# 设置为从库
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='<new-master-host>',
  SOURCE_PORT=3306,
  SOURCE_USER='<repl-user>',
  SOURCE_PASSWORD='<repl-password>',
  SOURCE_LOG_FILE='<new-binlog-file>',
  SOURCE_LOG_POS=<new-binlog-pos>;

START REPLICA;
```

## 有损切换（紧急）

当从库延迟 > 3 秒且核心业务受影响时执行：

1. 直接提升从库（接受数据丢失）
2. 记录切换时从库的 `Relay_Log_Pos`
3. 旧主库恢复后，使用 `pt-table-sync` 或 binlog 比对补齐差异数据
4. 严禁在未补齐数据前让旧主库重新接流

## 验证

- [ ] 新主库可读写
- [ ] 应用写入正常
- [ ] 延迟监控归零
- [ ] 旧主库作为从库加入，复制状态正常

## 后续

- 复盘切换原因，记录根因
- 评估是否需要自动切换工具（Orchestrator / MHA）
- 更新架构文档中的主从拓扑图