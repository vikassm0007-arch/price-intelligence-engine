"""
Day 26 — Distributed Scraper Node Cluster & Load Balancer
==========================================================
Learn & Practice distributed cluster node routing for price intelligence:
- Managing multi-region worker node pools (US-East, EU-Central, AP-South)
- Round-robin and load-balanced job distribution across scraper nodes
- Cluster node health monitoring & automatic node failover
"""

import random
import sys
import time
from typing import Any, Dict, List

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ScraperNode:

    def __init__(self, node_id: str, region: str, max_capacity: int = 5):
        self.node_id = node_id
        self.region = region
        self.max_capacity = max_capacity
        self.active_jobs = 0
        self.is_healthy = True

    def assign_job(self) -> bool:
        if self.is_healthy and self.active_jobs < self.max_capacity:
            self.active_jobs += 1
            return True
        return False

    def release_job(self):
        if self.active_jobs > 0:
            self.active_jobs -= 1


class DistributedClusterManager:

    def __init__(self):
        self.nodes = [
            ScraperNode("NODE-US-01", "US-East", max_capacity=5),
            ScraperNode("NODE-EU-01", "EU-Central", max_capacity=5),
            ScraperNode("NODE-AP-01", "AP-South", max_capacity=5),
        ]
        self.rr_index = 0

    def get_least_loaded_node(self) -> ScraperNode | None:
        """Selects the healthy node with the minimum active job load."""
        healthy_nodes = [n for n in self.nodes if n.is_healthy and n.active_jobs < n.max_capacity]
        if not healthy_nodes:
            return None
        return min(healthy_nodes, key=lambda n: n.active_jobs)

    def dispatch_url(self, url: str) -> Dict[str, Any] | None:
        node = self.get_least_loaded_node()
        if not node:
            print(f"⚠️ [Cluster Cluster] All nodes busy! Backpressuring request for {url}")
            return None

        node.assign_job()
        print(f"🛰️ [Cluster Routing] Routed {url} ➔ Node '{node.node_id}' ({node.region}) | Load: {node.active_jobs}/{node.max_capacity}")
        
        # Simulate execution
        time.sleep(0.1)
        node.release_job()

        return {
            "node_id": node.node_id,
            "region": node.region,
            "url": url,
            "status": "SUCCESS",
        }


def run_day_26_demo():
    print("[Day 26] Running Distributed Scraper Node Cluster & Load Balancer Engine...\n")
    cluster = DistributedClusterManager()

    urls = [
        "http://books.toscrape.com/catalogue/page-1.html",
        "http://books.toscrape.com/catalogue/page-2.html",
        "http://books.toscrape.com/catalogue/page-3.html",
        "http://books.toscrape.com/catalogue/page-4.html",
    ]

    for u in urls:
        cluster.dispatch_url(u)

    print("\n✅ Cluster execution and load balancing completed successfully.")


if __name__ == "__main__":
    run_day_26_demo()
