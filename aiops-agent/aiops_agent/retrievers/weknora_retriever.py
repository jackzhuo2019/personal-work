"""WeKnora knowledge base retriever — queries the ops knowledge base for relevant playbooks."""
import logging
import requests
from typing import Optional
from ..config_loader import Settings
from ..models import RetrievalResult

logger = logging.getLogger(__name__)


class WeKnoraRetriever:
    """Retrieves relevant playbooks from WeKnora knowledge base."""

    def __init__(self, settings: Settings):
        self.url = settings.weknora.url
        self.api_key = settings.weknora.api_key
        self.kb_id = settings.weknora.knowledge_base_id
        self.top_k = settings.weknora.search_top_k
        self.timeout = 30

    def search(self, query: str, top_k: Optional[int] = None) -> list[RetrievalResult]:
        """Search the knowledge base for relevant playbooks.

        Args:
            query: Natural language query (e.g. "磁盘满了怎么处理")
            top_k: Override default top_k

        Returns:
            List of retrieval results sorted by relevance.
        """
        k = top_k or self.top_k
        try:
            resp = requests.post(
                f"{self.url}/api/v1/knowledge-search",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "knowledge_base_ids": [self.kb_id],
                    "match_count": k,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()

            results: list[RetrievalResult] = []
            for item in data.get("data", []):
                results.append(RetrievalResult(
                    query=query,
                    content=item.get("content", ""),
                    source=item.get("knowledge_filename", item.get("knowledge_title", "unknown")),
                    score=item.get("score", 0.0),
                    knowledge_id=item.get("knowledge_id", ""),
                ))

            logger.info(f"WeKnora search [{query}] returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"WeKnora search failed [{query}]: {e}")
            return []

    def search_for_anomaly(self, anomaly_description: str, anomaly_type: str) -> list[RetrievalResult]:
        """Construct a query from an anomaly and search for relevant playbooks.

        Args:
            anomaly_description: Human-readable anomaly description
            anomaly_type: Type of anomaly (e.g. "high_disk")

        Returns:
            List of retrieval results.
        """
        # Build a natural language query from the anomaly
        query_map = {
            "high_cpu": "节点 CPU 使用率过高如何排查",
            "high_memory": "节点内存使用率过高如何排查",
            "high_disk": "磁盘满了怎么处理 磁盘使用率过高",
            "pod_restart": "Pod 频繁重启 CrashLoopBackOff 排查",
            "pod_not_ready": "Pod NotReady 状态异常排查",
            "high_http_5xx": "HTTP 5xx 错误率升高排查",
            "redis_high_mem": "Redis 内存溢出 内存使用率过高排查",
            "mysql_slave_lag": "MySQL 主从延迟 从库同步延迟排查",
            "service_down": "服务不可用 宕机 故障处理",
        }

        query = query_map.get(anomaly_type, anomaly_description)
        return self.search(query)