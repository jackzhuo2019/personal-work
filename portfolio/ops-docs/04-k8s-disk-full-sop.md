# K8s 节点磁盘满应急处理 SOP

## 适用场景

Kubernetes 节点磁盘使用率超过 85%，触发 P1 告警，可能导致 Pod 驱逐、容器写入失败、Kubelet 异常。

## 紧急处理（5 分钟内）

### 1. 确认磁盘状态

```bash
ssh <node-ip>
df -h / /var/lib/docker /var/lib/kubelet
```

### 2. 快速释放空间（按安全等级排序）

#### 2.1 清理未使用的 Docker 镜像和容器（最安全）

```bash
# 清理悬空镜像（<none> tag）
docker image prune -f

# 清理停止的容器
docker container prune -f

# 清理未使用的卷（需确认无容器引用）
docker volume prune -f

# 综合清理（谨慎，会删除所有未被容器使用的镜像）
docker system prune -a -f --volumes
```

#### 2.2 清理 K8s 已完成的 Pod 日志

```bash
# 清理退出的 Pod 容器日志
crictl rm --state exited --all 2>/dev/null || true

# 清理容器日志（大型文件）
find /var/log/containers -name "*.log" -size +100M -exec truncate -s 0 {} \;

# 清理 Docker JSON 日志
truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

#### 2.3 清理系统日志

```bash
# 清理 journalctl 日志
journalctl --vacuum-size=100M

# 清理 apt 缓存
apt-get clean
```

### 3. 确认 Kubelet 正常

```bash
systemctl status kubelet
kubectl get nodes | grep <node-name>
# 确认节点状态为 Ready
```

## 深层排查（30 分钟内）

### 查找大文件

```bash
# 查找最大的 20 个文件
find / -type f -size +500M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20

# 查找最大的目录
du -sh /* 2>/dev/null | sort -rh | head -10
du -sh /var/lib/docker/* 2>/dev/null | sort -rh | head -10
```

### 常见根因

#### 根因 1：容器日志无限增长

- 现象：`/var/lib/docker/containers/` 占用大量空间
- 根本解：配置 Docker 日志轮转

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

#### 根因 2：K8s emptyDir 或 emptyDir 大量数据

```bash
# 检查 emptyDir 使用
kubectl describe pod <pod-name> | grep -A5 "Volumes"
# 检查 Pod 的临时存储使用
kubectl describe pod <pod-name> | grep "Used\|Capacity"
```

#### 根因 3：镜像堆积

```bash
# 列出镜像
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -rh
# 清理旧版本镜像
docker rmi $(docker images --filter "dangling=true" -q)
```

#### 根因 4：CoreDump 文件

```bash
find / -name "core.*" -o -name "coredump.*" 2>/dev/null | head -10
rm -f /var/lib/systemd/coredump/*
```

## 预防措施

1. **日志轮转**：Docker daemon.json 配置 max-size + max-file
2. **告警阈值**：磁盘使用率 70% 预警（P2），85% 告警（P1）
3. **定时清理**：cron 定期执行 `docker system prune` + journalctl vacuum
4. **emptyDir 限制**：为 emptyDir 设置 sizeLimit

## 升级条件

- 磁盘满导致 Pod 驱逐且自动调度失败 → 升级 P0
- 多节点同时磁盘满（可能根因相同）→ 立即升级，拉群排查