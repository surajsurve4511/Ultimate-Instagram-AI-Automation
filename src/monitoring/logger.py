"""
Simple logger for monitoring events.
"""
import logging

logging.basicConfig(level=logging.INFO)

def log_event(message: str):
    logging.info(message)
