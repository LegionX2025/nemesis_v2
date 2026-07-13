import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("NEMESIS_JOB_ENGINE")

class JobManager:
    """
    Enterprise Orchestration Job Manager.
    Tracks background tasks across the platform.
    """
    def __init__(self):
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        
    def create_job(self, job_type: str, user: str, params: Dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        self.active_jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "status": "PENDING",
            "progress": 0,
            "message": "Job initialized",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "user": user,
            "params": params,
            "result": None
        }
        logger.info(f"Created Job {job_id} of type {job_type} for user {user}")
        return job_id
        
    def update_job(self, job_id: str, status: str, progress: int, message: str = "", result: Any = None):
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job["status"] = status
            job["progress"] = progress
            job["message"] = message
            job["updated_at"] = datetime.utcnow().isoformat()
            if result:
                job["result"] = result
            logger.debug(f"Job {job_id} updated: {status} ({progress}%) - {message}")
            
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.active_jobs.get(job_id)
        
    def get_all_jobs(self) -> list:
        # Sort by most recent
        return sorted(self.active_jobs.values(), key=lambda x: x["created_at"], reverse=True)
        
job_manager = JobManager()
