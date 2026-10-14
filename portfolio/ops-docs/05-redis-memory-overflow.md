# Redis 内存溢出排查步骤

## 适用场景

Redis 实例内存使用率超过 90%，触发 P1 告警，可能导致 OOM 或写入失败。

## 快速诊断

### 1. 检查 Redis 内存状态

```bash
redis-cli -h <redis-host> -p <port> -a <password>

# 查看内存概况
INFO memory

# 关注：
# used_memory_human         — 实际使用内存
# used_memory_peak_human    — 历史峰值
# maxmemory_human           — 配置的上限
# mem_fragmentation_ratio   — 碎片率（>1.5 需关注）
# maxmemory_policy          — 淘汰策略
```

### 2. 定位大 Key

```bash
# 查看内存使用最多的 key（需 redis-cli --bigkeys 或工具）
redis-cli --bigkeys -h <redis-host> -p <port> -a <password>

# 或使用 memory usage（Redis 4.0+）
MEMORY USAGE <key>
```

### 3. 分析 Key 数量和类型分布

```bash
# 统计各 DB 的 key 数量
INFO keyspace

# 抽样查看 key
SCAN 0 COUNT 1000
```

## 常见根因与处理

### 根因 1：缓存未设置过期时间

- 现象：key 数量持续增长，不回收
- 排查：
  ```bash
  # 随机抽取 key 检查 TTL
  redis-cli -a <password> --scan | head -100 | xargs -I{} redis-cli -a <password> TTL {}
  ```
- 处理：为缓存类 key 设置合理 TTL
  ```
  EXPIRE <key> 3600
  ```

### 根因 2：大 Key（单个 value 过大）

- 现象：少数 key 占用大量内存（如一个 Hash 存了百万字段）
- 排查：
  ```bash
  redis-cli --bigkeys -h <host> -p <port> -a <password>
  ```
- 处理：
  - 临时：删除无用的大 key（`DEL <key>`，注意大 key 删除可能阻塞）
  - 安全删除：`UNLINK <key>`（Redis 4.0+，异步删除）
  - 长期：拆分大 key，改用分片 Hash 或分页

### 根因 3：淘汰策略配置不当

- 现象：内存达到 maxmemory 但不淘汰
- 排查：确认 `maxmemory-policy`
  ```
  CONFIG GET maxmemory-policy
  ```
- 常见策略：

| 策略 | 行为 | 适用场景 |
|---|---|---|
| `noeviction` | 写入报错，不删除任何 key | 持久化数据 |
| `allkeys-lru` | 淘汰最近最少使用的 key | 纯缓存 |
| `volatile-lru` | 只淘汰有 TTL 的 key | 混合场景 |
| `allkeys-lfu` | 淘汰使用频率最低的 key | 纯缓存（更好命中率） |

- 处理：纯缓存实例设为 `allkeys-lru`

### 根因 4：内存碎片率过高

- 现象：`used_memory` 远小于 `used_memory_rss`
- 排查：`mem_fragmentation_ratio > 1.5`
- 处理：
  ```
  # 在低峰期执行（可能短暂阻塞）
  MEMORY PURGE
  ```
  或重启 Redis（释放碎片，但有数据丢失风险）

## 紧急释放

当内存使用率 > 95% 且影响写入时：

```bash
# 1. 找到最大的 3 个 key，判断是否可安全删除
redis-cli --bigkeys

# 2. 安全删除非关键 key
UNLINK <big-key-1>
UNLINK <big-key-2>

# 3. 如果无法删除，临时调大 maxmemory
CONFIG SET maxmemory <new-value>

# 4. 持久化数据优先检查是否有多余的备份/缓存 key
SCAN 0 MATCH "cache:*" COUNT 1000
```

## 预防措施

1. **监控**：Prometheus 采集 `redis_memory_used_bytes / redis_memory_max_bytes`，> 80% 预警
2. **淘汰策略**：缓存实例统一 `allkeys-lru`，非缓存实例设合理 maxmemory
3. **Key TTL**：缓存类 key 必须设置 TTL，不设置 TTL 的 key 需评审
4. **大 Key 巡检**：每日自动运行 `--bigkeys` 检查，结果存档
5. **容量规划**：监控内存增长趋势，提前扩容