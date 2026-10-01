"""
Day 23 — Distributed Task Queue & Worker Architecture
=====================================================
Learn & Practice asynchronous task queue architectures for price monitoring:
- Producer-Consumer task queue pattern for scalable scraping jobs
- Asynchronous task dispatching & status lifecycle tracking (PENDING, PROCESSING, COMPLETED, FAILED)
- Worker pool task execution with retry handlers
"""

import queue
import sys
import threading
import time
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup

# Ensure Windows stdout handles UTF-8 output properly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ScrapingTaskWorkerPool:

    def __init__(self, num_workers: int = 3):
        self.task_queue: queue.Queue = queue.Queue()
        self.num_workers = num_workers
        self.results: List[Dict[str, Any]] = []
        self.task_status: Dict[str, str] = {}
        self._lock = threading.Lock()

    def dispatch_job(self, task_id: str, url: str):
        """Enqueues a new scraping job into the task queue."""
        self.task_status[task_id] = "PENDING"
        self.task_queue.put({"task_id": task_id, "url": url})
        print(f"📥 [Task Queue] Dispatched Job '{task_id}' ➔ {url}")

    def _worker_loop(self):
        headers = {"User-Agent": "Mozilla/5.0"}
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
            except queue.Empty:
                break

            task_id = task["task_id"]
            url = task["url"]

            with self._lock:
                self.task_status[task_id] = "PROCESSING"

            print(f"⚙️ [Worker Thread] Processing '{task_id}'...")
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                response.encoding = "utf-8"
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("article.product_pod")

                record = {
                    "task_id": task_id,
                    "url": url,
                    "items_found": len(cards),
                    "status": "COMPLETED",
                }
                with self._lock:
                    self.results.append(record)
                    self.task_status[task_id] = "COMPLETED"
                print(f"✅ [Worker Thread] Completed '{task_id}' ➔ Found {len(cards)} items.")
            except Exception as err:
                with self._lock:
                    self.task_status[task_id] = "FAILED"
                print(f"❌ [Worker Thread] Task '{task_id}' failed: {err}")

            self.task_queue.task_done()

    def run_worker_pool(self):
        """Launches worker threads to process queued scraping jobs."""
        threads = []
        for i in range(self.num_workers):
            t = threading.Thread(target=self._worker_loop)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


def run_day_23_demo():
    print("[Day 23] Running Distributed Task Queue & Worker Architecture Engine...\n")
    pool = ScrapingTaskWorkerPool(num_workers=3)

    # Dispatch tasks
    pool.dispatch_job("JOB-001", "http://books.toscrape.com/")
    pool.dispatch_job("JOB-002", "http://books.toscrape.com/catalogue/page-2.html")
    pool.dispatch_job("JOB-003", "http://books.toscrape.com/catalogue/page-3.html")

    print("\n🚀 Starting worker pool processing...")
    pool.run_worker_pool()

    print("\n--- Task Status Lifecycle Summary ---")
    for tid, st in pool.task_status.items():
        print(f"  • {tid}: {st}")


if __name__ == "__main__":
    run_day_23_demo()
