JOBS = [
    "stock_alerts",
    "email_retries",
    "reservation_expiration",
    "deferred_exports",
    "low_activity_backup",
]


def job_policy() -> dict[str, object]:
    return {
        "scheduler": "APScheduler",
        "jobs": JOBS,
        "idempotent": True,
        "blocking_main_flow": False,
        "external_integrations": False,
        "backup_jobs": True,
        "backup_mode": "local_sandbox_metadata_only",
        "deploy_executed": False,
    }


def should_run(job_name: str) -> bool:
    return job_name in JOBS
