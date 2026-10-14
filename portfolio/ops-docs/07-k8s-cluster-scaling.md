# K8s 集群扩容操作手册

## 适用场景

Kubernetes 集群容量不足（CPU/内存/节点数），需要新增节点以满足业务增长。

## 扩容决策

| 触发条件 | 行动 |
|---|---|
| 集群平均 CPU > 70% 持续 3 天 | 计划扩容（7 天内执行） |
| Pending Pod 因资源不足无法调度 | 紧急扩容 |
| 节点数 < 业务最低冗余要求 | 紧急扩容 |
| 新业务上线需要额外容量 | 计划扩容 |

## 扩容前准备

### 1. 确认扩容规格

- 节点规格（CPU / 内存 / 磁盘）
- 新增节点数量
- 网络规划（Pod CIDR、Service CIDR 是否充足）
- 与现有节点规格是否一致（推荐一致）

### 2. 基础环境准备

```bash
# 新节点初始化（Ansible 批量执行）
ansible-playbook -i inventory.ini playbooks/node-init.yml \
  -e "target=new-node-01"

# 检查项：
# - OS 版本一致
# - Docker/containerd 已安装
# - 内核参数已调优
# - 防火墙规则已配置
# - 时间同步（NTP/chrony）正常
# - DNS 解析正常
```

### 3. 确认集群当前状态

```bash
# 节点状态
kubectl get nodes -o wide

# Pod CIDR 分配情况
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}' | tr ' ' '\n'

# 检查是否还有可用 CIDR
# Master 上执行
kubectl get configmap kubeadm-config -n kube-system -o yaml | grep podSubnet
```

## 扩容操作

### 标准流程（kubeadm 集群）

#### 1. 生成加入命令

```bash
# 在 master 上执行
kubeadm token create --print-join-command
# 输出: kubeadm join <master-ip>:6443 --token xxx --discovery-token-ca-cert-hash sha256:xxx
```

#### 2. 新节点加入集群

```bash
# 在新节点上执行
kubeadm join <master-ip>:6443 --token xxx --discovery-token-ca-cert-hash sha256:xxx

# 确认节点加入
kubectl get nodes
# 等待状态变为 Ready（通常 1-3 分钟）
```

#### 3. 验证节点

```bash
# 检查节点详情
kubectl describe node <new-node-name>

# 确认：
# - Conditions: Ready = True
# - 容量正确（cpu/memory）
# - kubelet 正常运行
# - CNI 插件正常运行（Calico/Flannel Pod 已 Running）
```

#### 4. 打标签和污点

```bash
# 根据节点角色打标签
kubectl label node <new-node-name> node-role.kubernetes.io/worker=

# 如需隔离特定工作负载
kubectl label node <new-node-name> workload=general

# 如需设置污点（专用节点）
kubectl taint node <new-node-name> dedicated=worker:NoSchedule
```

## 扩容后验证

### 1. 功能验证

```bash
# 创建测试 Pod 确认调度到新节点
kubectl run nginx-test --image=nginx --restart=Never
kubectl get pod nginx-test -o wide
# 确认被调度到新节点

# 清理测试 Pod
kubectl delete pod nginx-test
```

### 2. 网络验证

```bash
# 新节点 Pod 到 Service 网络连通性
kubectl exec -it <pod-on-new-node> -- curl <service-ip>

# 新节点 Pod 到 Pod 跨节点通信
kubectl exec -it <pod-on-new-node> -- ping <pod-ip-on-other-node>

# DNS 解析
kubectl exec -it <pod-on-new-node> -- nslookup kubernetes.default
```

### 3. 监控接入验证

```bash
# 确认 node-exporter 已部署到新节点
kubectl get pod -n monitoring -o wide | grep <new-node-name>

# 在 Grafana 确认新节点指标可见
# 检查 Dashboard → Node Overview → 新节点是否出现
```

### 4. 告警规则覆盖

- 确认新节点的告警规则已自动覆盖（Prometheus 基于标签自动发现）
- 手动触发一个测试告警确认通知链路

## 回滚

如果新节点加入后出现问题：

```bash
# 1. 先排水（驱逐 Pod）
kubectl drain <new-node-name> --ignore-daemonsets --delete-emptydir-data

# 2. 确认 Pod 已迁移
kubectl get pods --field-selector spec.nodeName=<new-node-name>

# 3. 从集群移除
kubectl delete node <new-node-name>

# 4. 在新节点上 reset
kubeadm reset
```

## 注意事项

1. **滚动扩容**：一次最多加 2-3 个节点，确认稳定后再加下一批
2. **etcd 性能**：节点数超过 100 时关注 etcd 性能（etcd 是瓶颈）
3. **Pod CIDR 余量**：每个节点消耗一个 Pod CIDR 子网，提前规划
4. **负载均衡**：新节点自动加入 Service 负载均衡池，确认后端列表更新
5. **日志采集**：确认 Filebeat/Fluentd 已在新节点部署，日志能正常采集