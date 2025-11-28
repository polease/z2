"""
Job queue manager for processing jobs
"""
import asyncio
from typing import Dict
from .pipeline_runner import PipelineRunner


class JobQueueManager:
    """Manage job queue and worker pool"""

    def __init__(self, max_workers: int = 2):
        self.queue = asyncio.Queue()
        self.max_workers = max_workers
        self.active_jobs: Dict[int, asyncio.Task] = {}
        self.workers = []
        self.running = False

    async def start(self):
        """Start worker pool"""
        if self.running:
            return

        self.running = True
        self.workers = [
            asyncio.create_task(self.worker(i))
            for i in range(self.max_workers)
        ]
        print(f"✓ Started {self.max_workers} workers")

    async def stop(self):
        """Stop worker pool"""
        self.running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Cancel all active jobs
        for job_id, task in self.active_jobs.items():
            task.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
        self.active_jobs = {}
        print("✓ Stopped all workers")

    async def enqueue(self, job_id: int, youtube_url: str):
        """Add job to queue"""
        await self.queue.put((job_id, youtube_url))
        print(f"✓ Enqueued job {job_id}")

    async def cancel_job(self, job_id: int):
        """Cancel a running job"""
        if job_id in self.active_jobs:
            task = self.active_jobs[job_id]
            task.cancel()
            print(f"✓ Cancelled job {job_id}")

    async def worker(self, worker_id: int):
        """Worker process that pulls jobs from queue"""
        print(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get next job from queue (with timeout to allow graceful shutdown)
                try:
                    job_id, youtube_url = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                print(f"Worker {worker_id} processing job {job_id}")

                # Create and run pipeline
                runner = PipelineRunner(job_id, youtube_url)
                task = asyncio.create_task(runner.run())
                self.active_jobs[job_id] = task

                try:
                    await task
                except asyncio.CancelledError:
                    print(f"Job {job_id} was cancelled")
                except Exception as e:
                    print(f"Job {job_id} failed: {e}")
                finally:
                    # Remove from active jobs
                    if job_id in self.active_jobs:
                        del self.active_jobs[job_id]

                    self.queue.task_done()
                    print(f"Worker {worker_id} completed job {job_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        print(f"Worker {worker_id} stopped")


# Global job queue manager instance
job_queue_manager = JobQueueManager(max_workers=2)
