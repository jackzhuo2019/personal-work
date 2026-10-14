# K8s Pod 频繁重启排查 SOP

## 适用场景

Kubernetes 集群中 Pod 出现频繁重启（CrashLoopBackOff），影响服务可用性。

## 诊断步骤

### 1. 确认 Pod 状态

```bash
kubectl get pods -n <namespace> | grep -v Running
kubectl describe pod <pod-name> -n <namespace>
```

关注以下字段：
- `Restart Count`：重启次数，超过 3 次需立即排查
- `Last State`：上一次终止原因（Exit Code、Signal）
- `Events`：最近事件（Pulling、Created、Started、BackOff）

### 2. 查看容器日志

```bash
# 当前日志
kubectl logs <pod-name> -n <namespace> --tail=200

# 上一次崩溃的日志（关键）
kubectl logs <pod-name> -n <namespace> --previous --tail=200
```

常见 Exit Code 含义：

| Exit Code | 含义 | 常见原因 |
|---|---|---|
| 1 | 通用错误 | 应用启动失败、配置错误 |
| 137 | SIGKILL (128+9) | OOM Killed 或手动 kill |
| 139 | SIGSEGV (128+11) | 段错误，内存非法访问 |
| 143 | SIGTERM (128+15) | 正常终止信号，优雅退出 |

### 3. 检查资源限制

```bash
kubectl describe pod <pod-name> -n <namespace> | grep -A5 "Limits\|Requests"
```

- 如果 Exit Code = 137，优先检查是否 OOM Killed
- 查看 Node 级别内存压力：`kubectl describe node <node-name> | grep -A10 "Memory Pressure"`

### 4. 排查常见根因

#### 4.1 OOM Killed（最常见）

- 现象：Exit Code 137，`Last State` 显示 `OOMKilled`
- 处理：
  1. 检查 `resources.limits.memory` 是否设置过小
  2. 检查应用内存泄漏（Java 应用看 heap dump，Go 看 pprof）
  3. 临时调大 limit 观察，长期需修复代码或合理设置 limit

#### 4.2 健康检查失败

- 现象：`Liveness probe failed`
- 处理：
  1. 检查 liveness probe 配置（路径、端口、超时、阈值）
  2. 确认应用启动时间是否长于 `initialDelaySeconds`
  3. 区分 liveness 和 readiness：liveness 失败会重启，readiness 失败只会摘流

#### 4.3 配置/依赖错误

- 现象：Exit Code 1，日志有连接超时或配置找不到
- 处理：
  1. 检查 ConfigMap/Secret 是否正确挂载
  2. 检查依赖服务（DB、Redis、下游 API）是否可达
  3. 检查环境变量是否完整注入

#### 4.4 镜像问题

- 现象：`ImagePullBackOff` 或 `ErrImagePull`
- 处理：
  1. 确认镜像 tag 存在
  2. 检查 imagePullSecrets 配置
  3. 检查私有仓库网络连通性

## 升级条件

- Pod 在 30 分钟内重启超过 5 次，且无法通过上述步骤定位根因 → 升级到 SRE on-call
- 影响核心业务（坐席服务、呼叫路由）→ 立即升级，不等 30 分钟

## 恢复确认

故障排除后确认：
1. Pod 持续 Running 超过 10 分钟无重启
2. Ready 状态为 True
3. 服务接口返回正常
4. 监控告警恢复

## 记录

- 在工单系统记录：故障时间、影响范围、根因、处理步骤、恢复时间
- 如涉及架构改进，创建后续优化任务