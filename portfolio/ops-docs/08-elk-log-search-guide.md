# ELK 日志检索规范

## 适用场景

使用 Elasticsearch + Kibana 进行日志检索、故障排查和审计。

## 日志索引结构

### 索引命名规范

```
{environment}-{service}-{date}
# 示例: prod-contact-center-2026.10.13
# 示例: staging-api-gateway-2026.10.13
```

### 关键字段约定

| 字段 | 类型 | 说明 |
|---|---|---|
| `@timestamp` | date | 日志时间（UTC） |
| `level` | keyword | INFO / WARN / ERROR / DEBUG |
| `service` | keyword | 服务名（contact-center, api-gateway 等） |
| `env` | keyword | prod / staging / dev |
| `host` | keyword | 主机名 |
| `pod` | keyword | K8s Pod 名 |
| `trace_id` | keyword | 链路追踪 ID |
| `request_id` | keyword | 请求 ID |
| `message` | text | 日志正文 |
| `error_code` | keyword | 错误码 |

## 常用检索场景

### 1. 按 trace_id 查全链路日志

```json
// Kibana KQL
trace_id: "abc123def456"
```

快速定位单次请求在所有服务中的完整日志链路。

### 2. 按错误级别 + 服务过滤

```json
level: "ERROR" and service: "contact-center" and @timestamp > "2026-10-13T00:00:00Z"
```

### 3. 按错误码聚合

```json
level: "ERROR" and error_code: "CALL_TIMEOUT_503"

// 聚合：按 error_code 统计
# 在 Kibana Visualize 中：
# X-Axis: terms aggregation on error_code
# Y-Axis: count
```

### 4. 按时间范围 + 关键词

```json
message: "database connection failed" and @timestamp >= "2026-10-13T14:00:00Z" and @timestamp < "2026-10-13T15:00:00Z"
```

### 5. 排查 Pod 重启

```json
pod: "contact-center-*" and level: "ERROR" and @timestamp > "now-30m"
```

## 日志检索最佳实践

### 查询优化

1. **优先使用 keyword 字段**：`level`、`service`、`error_code` 是 keyword 类型，查询快
2. **text 字段用 match 不用 term**：`message` 是 text 类型，用 `match` 而非 `term`
3. **时间范围必加**：不加时间范围会全索引扫描，极慢
4. **避免通配符开头**：`service: "*center"` 性能极差，改用 `service: "contact-center"`
5. **用 trace_id 而非 message 搜**：链路 ID 是 keyword，精确匹配

### 索引策略

| 配置 | 值 | 原因 |
|---|---|---|
| 分片数 | 3 | 单日日志量约 5GB，3 分片足够 |
| 副本数 | 1 | 高可用 |
| 保留天数（prod） | 30 天 | 满足审计要求，控制存储 |
| 保留天数（staging） | 7 天 | 节约存储 |
| 滚动策略 | ILM | 自动滚动 + 删除 |

### ILM 策略

```json
{
  "policy": "logs-policy",
  "phases": {
    "hot": {
      "actions": {
        "rollover": {
          "max_size": "10gb",
          "max_age": "1d"
        }
      }
    },
    "delete": {
      "min_age": "30d",
      "actions": { "delete": {} }
    }
  }
}
```

## 常见问题排查

### 问题 1：日志查不到

1. 确认时间范围正确（注意 UTC vs 本地时间，差 8 小时）
2. 确认索引模式正确（在 Kibana Stack Management → Index Patterns）
3. 确认日志级别过滤器没误过滤
4. 检查 Logstash/Filebeat 是否正常采集

### 问题 2：检索很慢

1. 加上时间范围（最常见的慢查询原因）
2. 用 keyword 字段替代 text 字段过滤
3. 检查分片数是否合理（单分片 > 50GB 需重新分片）
4. 考虑用异步搜索（Async Search）

### 问题 3：日志丢失

1. 检查 Filebeat/Fluentd 容器状态
2. 检查 K8s Pod 日志是否被轮转清除（docker logs 配置）
3. 检查 Elasticsearch 是否有磁盘满告警（会导致写入拒绝）
4. 检查 Logstash 是否有 backlog

## 日志安全

- 敏感信息（手机号、身份证、密码）禁止写入日志
- 如已写入，使用 Logstash 的 filter 进行脱敏（gsub/mutate）
- 审计日志单独索引，保留 90 天以上