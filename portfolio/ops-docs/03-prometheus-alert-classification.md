# Prometheus 告警分级与响应流程

## 告警分级标准

### P0 — 紧急（立即响应，全员投入）

| 告警 | 条件 | 响应时间 |
|---|---|---|
| 核心服务宕机 | `up == 0` for 2min | ≤ 5 分钟 |
| 坐席系统全量不可用 | 可用坐席 < 阈值的 50% | ≤ 5 分钟 |
| 数据库主库不可达 | `mysql_up == 0` | ≤ 5 分钟 |
| 呼叫路由服务中断 | 呼叫成功率 < 80% | ≤ 5 分钟 |

**响应**：电话通知 on-call + IM 群 @全员 + 自动创建 P0 工单

### P1 — 严重（10 分钟内响应）

| 告警 | 条件 | 响应时间 |
|---|---|---|
| 单节点宕机 | `node_down == 1` for 3min | ≤ 10 分钟 |
| K8s Pod 重启频繁 | `kube_pod_container_status_restarts_total` > 5 | ≤ 10 分钟 |
| 磁盘使用率 > 85% | `node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.15` | ≤ 10 分钟 |
| P99 延迟超阈值 | `histogram_quantile(0.99, ...) > 阈值` | ≤ 10 分钟 |
| Redis 内存使用率 > 90% | `redis_memory_used_bytes / redis_memory_max_bytes > 0.9` | ≤ 10 分钟 |

**响应**：IM 群 @on-call + 自动创建 P1 工单

### P2 — 警告（30 分钟内响应）

| 告警 | 条件 | 响应时间 |
|---|---|---|
| CPU 使用率 > 80% 持续 10 分钟 | `rate(node_cpu_seconds_total{mode="idle"}[10m]) < 0.2` | ≤ 30 分钟 |
| 内存使用率 > 75% | `1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.75` | ≤ 30 分钟 |
| HTTP 5xx 率 > 1% | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01` | ≤ 30 分钟 |
| Kafka 消费延迟 > 10000 条 | `kafka_consumergroup_lag > 10000` | ≤ 30 分钟 |

**响应**：IM 群通知 + 自动创建 P2 工单

### P3 — 通知（工作时间处理）

| 告警 | 条件 | 响应时间 |
|---|---|---|
| 非核心节点磁盘 > 70% | 同上 | 工作时间内 |
| 非高峰期 CPU > 60% | 同上 | 工作时间内 |
| 证书即将过期 | < 30 天 | 工作时间内 |
| 非核心日志告警 | 日志级别 WARN 持续 | 工作时间内 |

**响应**：IM 群通知 + 工单系统自动创建

## 告警降噪规则

### 聚合规则

- 同一 Node 上的多个 Pod 告警 → 聚合为 1 条（根因可能在 Node 级别）
- 同一服务的多实例告警 → 当实例存活数 > 50% 时不告警（自愈）
- 告警风暴（> 20 条/分钟）→ 抑制低优先级告警，只保留 P0/P1

### 抑制规则（Inhibit Rules）

```yaml
# 如果 P0 告警触发，抑制同 scope 的 P2/P3
- source_matchers: ['severity = "P0"']
  target_matchers: ['severity =~ "P2|P3"']
  equal: ['cluster', 'service']
```

## On-Call 响应流程

1. **收到告警** → 确认告警内容和级别
2. **P0/P1** → 在 IM 群回复"收到，开始排查"（让团队知道有人在处理）
3. **排查** → 按 SOP/playbook 执行
4. **P0 且 5 分钟未恢复** → 拉群，通知上级
5. **恢复后** → 在 IM 群同步"已恢复 + 根因摘要"
6. **工单闭环** → 填写根因、处理步骤、改进措施

## 告警审计

每周审查：
- P0/P1 告警是否有 SOP/playbook 对应
- 是否有频繁误触发的告警规则需调优
- MTTR 趋势是否恶化