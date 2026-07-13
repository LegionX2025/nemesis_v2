import logging
import asyncio
from typing import Dict, Any
from .manager import job_manager

logger = logging.getLogger("NEMESIS_JOB_WORKERS")

async def mock_long_running_task(job_id: str, duration: int = 10):
    """A simulated long-running task to demonstrate job tracking."""
    job_manager.update_job(job_id, "RUNNING", 10, "Task started...")
    
    for i in range(duration):
        await asyncio.sleep(1)
        progress = int(10 + ((i / duration) * 80))
        job_manager.update_job(job_id, "RUNNING", progress, f"Processing step {i+1}/{duration}")
        
    job_manager.update_job(job_id, "COMPLETED", 100, "Task completed successfully", {"result_code": "OK"})

async def execute_job(job_id: str, job_type: str, params: Dict[str, Any]):
    """
    Main entry point for background execution. 
    Routes to the specific worker logic based on job_type.
    """
    try:
        if job_type == "osint_sweep":
            target = params.get("target", "unknown")
            logger.info(f"Starting OSINT Sweep worker for {target}")
            # Mocking the actual OSINT logic for phase 2 scaffold
            await mock_long_running_task(job_id, duration=5)
            
        elif job_type == "blockchain_sync":
            network = params.get("network", "ethereum")
            logger.info(f"Starting Blockchain Sync worker for {network}")
            await mock_long_running_task(job_id, duration=15)
            
        elif job_type == "sanctions_refresh":
            logger.info(f"Starting Sanctions Refresh worker")
            await mock_long_running_task(job_id, duration=8)
            
        else:
            logger.warning(f"Unknown job type requested: {job_type}")
            job_manager.update_job(job_id, "FAILED", 0, f"Unknown job type: {job_type}")
            
    except Exception as e:
        logger.error(f"Job {job_id} failed with error: {e}")
        job_manager.update_job(job_id, "FAILED", 0, f"Internal Error: {str(e)}")
