# 每日巡检清单与标准

## 巡检时间

- 每日 09:00 自动执行巡检脚本
- 巡检报告发送至 IM 群 + 工单系统
- 异常项需在 30 分钟内确认处理

## 巡检项目

### 1. 集群节点状态

```bash
# K8s 节点状态
kubectl get nodes -o wide

# 检查标准
# - 所有节点 Ready = True
# - 无 NotReady 节点
# - 无版本不一致（除非在滚动升级中）
```

| 指标 | 正常 | 预警 | 告警 |
|---|---|---|---|
| Ready 节点数 / 总节点数 | 100% | — | < 100% |
| NotReady 持续时间 | — | < 5min | > 5min |

### 2. Pod 状态

```bash
# 统计 Pod 状态
kubectl get pods --all-namespaces -o wide | grep -v Running

# 非正常状态的 Pod 数
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded | wc -l
```

| 指标 | 正常 | 预警 | 告警 |
|---|---|---|---|
| 非 Running Pod 数 | 0 | 1-3 | > 3 |
| CrashLoopBackOff Pod | 0 | 1 | > 1 |
| Pending Pod（无资源调度） | 0 | 1-2 | > 2 |

### 3. 资源使用率

```bash
# 通过 Prometheus 查询
# CPU 使用率
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 磁盘使用率
1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100
```

| 指标 | 正常 | 预警（P2） | 告警（P1） |
|---|---|---|---|
| CPU 使用率 | < 60% | 60-80% | > 80% |
| 内存使用率 | < 70% | 70-85% | > 85% |
| 磁盘使用率 | < 60% | 60-85% | > 85% |
| Inode 使用率 | < 60% | 60-85% | > 85% |

### 4. 数据库健康

| 检查项 | 命令 | 正常 |
|---|---|---|
| MySQL 主从状态 | `SHOW SLAVE STATUS\G` | IO/SQL Running: Yes，延迟 < 3s |
| MySQL 慢查询数 | Prometheus: `mysql_slow_queries` | 增速 < 10/min |
| Redis 连接数 | `INFO clients` | < maxclients * 0.8 |
| Redis 内存 | `INFO memory` | < maxmemory * 0.85 |
| Kafka 消费延迟 | `kafka_consumergroup_lag` | < 1000 条 |

### 5. 中间件健康

```bash
# 检查所有中间件容器状态
kubectl get pods -n middleware

# 关键中间件清单
# - MySQL (主 + 从)
# - Redis (主 + 哨兵)
# - Kafka (所有 Broker)
# - RabbitMQ (主 + 从)
# - ELK (Elasticsearch + Kibana + Logstash)
# - Nginx Ingress Controller
```

### 6. 证书有效期

```bash
# K8s 集群证书
kubeadm certs check-expiration

# Ingress TLS 证书
kubectl get secret -A | grep tls
# 检查过期时间
echo | openssl s_client -connect <domain>:443 2>/dev/null | openssl x509 -noout -dates
```

| 指标 | 正常 | 预警 | 告警 |
|---|---|---|---|
| 证书剩余天数 | > 30 天 | 15-30 天 | < 15 天 |

### 7. 备份验证

| 检查项 | 标准 |
|---|---|
| 昨日 MySQL 备份文件存在 | ✅ |
| 备份文件大小 > 昨天的 80% | ✅ |
| 备份恢复测试（每周一次） | ✅ |
| Elasticsearch 快照完成 | ✅ |

### 8. 业务指标

| 指标 | 正常 | 预警 | 告警 |
|---|---|---|---|
| 坐席在线率 | > 95% | 90-95% | < 90% |
| 呼叫成功率 | > 99% | 95-99% | < 95% |
| API P99 延迟 | < 500ms | 500-1000ms | > 1000ms |
| HTTP 5xx 率 | < 0.1% | 0.1-1% | > 1% |

## 巡检报告格式

```
【每日巡检报告】2026-10-13 09:00

集群状态：✅ 正常
节点：48/48 Ready
Pod：256 Running, 0 Abnormal
CPU 平均：42% | 内存平均：63% | 磁盘平均：51%

数据库：✅
- MySQL 主从延迟: 0s
- Redis 内存: 68%
- Kafka 消费延迟: 120 条

中间件：✅ 全部 Running
证书：最小剩余 45 天 ✅
备份：昨日 MySQL 备份完成 ✅

业务指标：✅
- 坐席在线率: 97.2%
- 呼叫成功率: 99.3%
- API P99: 320ms

异常项：无
巡检人：自动化 + on-call 确认
```