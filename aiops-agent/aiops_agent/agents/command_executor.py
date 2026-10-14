"""Command execution layer — L0 read-only diagnostic commands with whitelist enforcement."""
import logging
import os
import shlex
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ActionLevel(str, Enum):
    """Permission levels for agent actions."""
    L0 = "L0"  # Read-only, auto-execute
    L1 = "L1"  # Diagnostic, auto-execute
    L2 = "L2"  # Light operation, requires human approval
    L3 = "L3"  # Heavy operation, requires human approval
    L4 = "L4"  # Dangerous, never execute


@dataclass
class CommandResult:
    """Result of an executed command."""
    command: str
    level: ActionLevel
    exit_code: int
    stdout: str
    stderr: str
    executed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_by: str = "auto"  # "auto" or "human:<name>"
    truncated: bool = False
    error: str = ""

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    def summary(self, max_chars: int = 500) -> str:
        """Short summary of output for LLM context."""
        output = self.stdout.strip() or self.stderr.strip()
        if len(output) > max_chars:
            return output[:max_chars] + "\n... [truncated]"
        return output


# ── Whitelist ──────────────────────────────────────────────

# L0: Read-only kubectl commands — safe to auto-execute
_L0_KUBECTL = {
    "get": True,       # kubectl get pods/nodes/services
    "describe": True,  # kubectl describe pod/node
    "logs": True,      # kubectl logs (including --previous)
    "top": True,       # kubectl top pods/nodes
    "events": True,    # kubectl get events
    "version": True,
    "cluster-info": True,
}

# L0: Read-only system commands
_L0_SYSTEM = {
    "df": True,
    "free": True,
    "uptime": True,
    "top": True,      # top -bn1
    "hostname": True,
    "cat": True,      # only specific safe paths
}

# L0: Safe cat paths
_L0_CAT_PATHS = {
    "/proc/loadavg",
    "/proc/meminfo",
    "/etc/os-release",
}

# L2: Light operations — require approval
_L2_COMMANDS = {
    "kubectl delete pod",
    "docker image prune",
    "docker container prune",
    "docker system prune",
    "journalctl --vacuum-size",
    "truncate -s 0",
}

# Forbidden patterns — never allowed
_FORBIDDEN_PATTERNS = [
    "kubectl delete node",
    "kubectl delete deployment",
    "kubectl delete service",
    "kubectl delete configmap",
    "kubectl delete secret",
    "kubectl delete namespace",
    "kubectl scale",
    "kubectl cordon",
    "kubectl drain",
    "kubectl apply",
    "kubectl edit",
    "kubectl exec",  # exec into container — L1, handled separately
    "rm -rf /",
    "shutdown",
    "reboot",
    "iptables",
    "iptables-restore",
]


class CommandExecutor:
    """Executes diagnostic commands with whitelist enforcement.

    Only L0 (read-only) commands are auto-executed.
    L1+ commands are proposed but not executed — they require human approval.
    """

    def __init__(self, timeout: int = 15, kubectl_path: str = ""):
        self.timeout = timeout
        # Find kubectl binary: explicit path > common paths > PATH
        self.kubectl = kubectl_path or self._find_kubectl()

    def _find_kubectl(self) -> str:
        """Find kubectl binary path."""
        candidates = [
            "/usr/local/bin/kubectl",
            "/opt/kube/bin/kubectl",
            "/usr/bin/kubectl",
        ]
        for p in candidates:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
        # Fall back to PATH
        return "kubectl"

    def _resolve_command(self, command: str) -> str:
        """Replace 'kubectl' with the full path if configured."""
        if self.kubectl and self.kubectl != "kubectl":
            # Replace only the leading 'kubectl' token
            if command.strip().startswith("kubectl "):
                return self.kubectl + command[7:]
            if command.strip() == "kubectl":
                return self.kubectl
        return command

    def classify(self, command: str) -> ActionLevel:
        """Classify a command into an action level.

        Returns L4 for anything not in the whitelist.
        """
        cmd = command.strip()

        # Check forbidden patterns first
        for pattern in _FORBIDDEN_PATTERNS:
            if pattern in cmd:
                return ActionLevel.L4

        # Parse command
        try:
            parts = shlex.split(cmd)
        except ValueError:
            return ActionLevel.L4

        if not parts:
            return ActionLevel.L4

        binary = parts[0]

        # kubectl commands
        if binary == "kubectl":
            if len(parts) < 2:
                return ActionLevel.L4

            subcmd = parts[1]

            # kubectl exec — L1 (read-only exec into containers)
            if subcmd == "exec":
                # Only allow read-only commands inside exec
                # e.g. kubectl exec pod -- ps aux, kubectl exec pod -- cat /etc/config
                return ActionLevel.L1

            # L0 kubectl subcommands
            if subcmd in _L0_KUBECTL:
                return ActionLevel.L0

            # Check for L2 delete pod
            if subcmd == "delete" and len(parts) > 2 and parts[2] == "pod":
                return ActionLevel.L2

            return ActionLevel.L4

        # System commands
        if binary in _L0_SYSTEM:
            if binary == "cat":
                # Only allow specific safe paths
                for arg in parts[1:]:
                    if arg.startswith("-"):
                        continue
                    if arg not in _L0_CAT_PATHS:
                        return ActionLevel.L4
            return ActionLevel.L0

        # Check L2 patterns
        for pattern in _L2_COMMANDS:
            if cmd.startswith(pattern):
                return ActionLevel.L2

        # Unknown command — treat as forbidden
        return ActionLevel.L4

    def can_execute(self, command: str) -> bool:
        """Check if a command can be auto-executed (L0 or L1)."""
        level = self.classify(command)
        return level in (ActionLevel.L0, ActionLevel.L1)

    def execute(self, command: str) -> CommandResult:
        """Execute an L0/L1 command. Returns CommandResult.

        For L2+ commands, returns a result with error="requires human approval".
        """
        level = self.classify(command)

        if level == ActionLevel.L4:
            return CommandResult(
                command=command,
                level=level,
                exit_code=-1,
                stdout="",
                stderr="",
                error="Command is forbidden (L4). Not in whitelist.",
            )

        if level == ActionLevel.L2 or level == ActionLevel.L3:
            return CommandResult(
                command=command,
                level=level,
                exit_code=-1,
                stdout="",
                stderr="",
                error=f"Command requires human approval ({level.value}). Proposed but not executed.",
            )

        # L0 or L1 — safe to execute
        resolved = self._resolve_command(command)
        logger.info(f"Executing [{level.value}]: {command}")

        try:
            proc = subprocess.run(
                shlex.split(resolved),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                stdin=subprocess.DEVNULL,
            )

            # Truncate large outputs
            max_output = 8000
            stdout = proc.stdout
            stderr = proc.stderr
            truncated = False

            if len(stdout) > max_output:
                stdout = stdout[:max_output] + "\n... [output truncated]"
                truncated = True

            result = CommandResult(
                command=command,
                level=level,
                exit_code=proc.returncode,
                stdout=stdout,
                stderr=stderr,
                truncated=truncated,
            )

            logger.info(f"Command completed [{level.value}] exit={proc.returncode}: {command[:80]}")
            return result

        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                level=level,
                exit_code=-1,
                stdout="",
                stderr="",
                error=f"Command timed out after {self.timeout}s",
            )
        except Exception as e:
            return CommandResult(
                command=command,
                level=level,
                exit_code=-1,
                stdout="",
                stderr="",
                error=f"Execution failed: {e}",
            )

    def execute_batch(self, commands: list[str]) -> list[CommandResult]:
        """Execute multiple commands. Only L0/L1 are executed; L2+ are proposed."""
        results: list[CommandResult] = []
        for cmd in commands:
            results.append(self.execute(cmd))
        return results

    def build_investigation_plan(self, anomaly_type: str, target: str, metadata: dict) -> list[str]:
        """Build a list of L0 diagnostic commands to investigate an anomaly.

        This is the default investigation path — the LLM can override or extend it.
        """
        commands: list[str] = []
        ns = metadata.get("namespace", "")
        pod = metadata.get("pod", "")
        node = metadata.get("node", "")

        if anomaly_type in ("pod_restart", "pod_not_ready"):
            if pod and ns:
                commands.extend([
                    f"kubectl describe pod {pod} -n {ns}",
                    f"kubectl logs {pod} -n {ns} --tail=100",
                    f"kubectl logs {pod} -n {ns} --previous --tail=100",
                ])
            commands.append("kubectl get events --sort-by=.lastTimestamp")

        elif anomaly_type in ("high_cpu", "high_memory", "high_disk"):
            if node:
                commands.extend([
                    f"kubectl describe node {node}",
                    f"kubectl top pods --sort-by=cpu -A | head -20",
                    f"kubectl top pods --sort-by=memory -A | head -20",
                ])
            if anomaly_type == "high_disk" and node:
                commands.extend([
                    f"kubectl get pods --field-selector spec.nodeName={node} -A",
                ])

        elif anomaly_type == "service_down":
            commands.extend([
                "kubectl get pods -A | grep -v Running",
                "kubectl get events --sort-by=.lastTimestamp",
            ])

        # Always add a general cluster check
        commands.append("kubectl get nodes -o wide")

        return commands