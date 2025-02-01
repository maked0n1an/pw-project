import asyncio
import logging
import random
from typing import Optional


async def sleep(
    seconds: float,
    inner_logger: Optional[logging.Logger] = None,
    custom_msg: Optional[str] = None,
) -> None:
    wait_msg = f'Sleeping for {seconds} seconds...'
    log_msg = f'{custom_msg}. {wait_msg}' if custom_msg else wait_msg
    
    if (logger := inner_logger):
        logger.info(log_msg)
        
    await asyncio.sleep(seconds)


async def sleep_by_range(
    delay: tuple[float, float],
    logger: Optional[logging.Logger] = None,
    custom_msg: Optional[str] = None,
) -> None:
    min_delay, max_delay = delay
    delay_to_sleep = random.uniform(min_delay, max_delay)
    await sleep(delay_to_sleep, logger, custom_msg)
