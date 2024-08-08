"""Main!"""

import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()
stage = os.getenv("STAGE")


def hello_world() -> str:
    """Hello World"""
    logger.critical(f"critical - {stage}", stage)
    logger.debug(f"debug - {stage}", stage)
    logger.error(f"error - {stage}", stage)
    logger.exception(f"exception - {stage}", stage)
    logger.info(f"info - {stage}", stage)
    logger.success(f"success - {stage}", stage)
    logger.trace(f"trace - {stage}", stage)
    logger.warning(f"warning - {stage}", stage)
    return "Hello World"


if __name__ == "__main__":
    hello_world()
