"""
Prefect flow definition for scheduled jobs.
"""
from prefect import flow

from src.orchestrator.main import run_job

def scheduled_job():
@flow
def scheduled_job():
    # Example: run with a fixed topic or from a queue
    run_job("Instagram automation: AI-generated art")
