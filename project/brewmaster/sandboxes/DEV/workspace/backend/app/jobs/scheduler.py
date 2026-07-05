JOBS = [
    "stock_alerts",
    "email_retries",
    "reservation_expiration",
    "deferred_exports",
    "low_activity_backup",
]


def job_policy() -> dict[str, object]:
    return {"scheduler": "APScheduler", "jobs": JOBS, "idempotent": True, "blocking_main_flow": False}
