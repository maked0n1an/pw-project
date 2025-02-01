import asyncio
import logging
import os
import sys

from patchright.async_api import async_playwright
from dotenv import load_dotenv

from src.modules.openion_pw.openion import Openion
from src.managers.rabby_wallet_pw.types import Config
from src.managers.rabby_wallet_pw.rabby_wallet import RabbyWalletWithPlaywright


main_logger = logging.getLogger('main')
main_logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
main_logger.addHandler(console_handler)

file_handler = logging.FileHandler(f"rabby.log")
file_handler.setLevel(logging.DEBUG)
main_logger.addHandler(file_handler)

logger = main_logger
load_dotenv()

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
EXTENSION_PATH = os.path.join(os.path.dirname(__file__), 'Rabby_v0.93.12')


async def import_rabby_wallet():
    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir='',
            channel='chromium',
            args=[
                f'--disable-extensions-except={EXTENSION_PATH}',
                f'--load-extension={EXTENSION_PATH}',
                '--disable-blink-features=AutomationControlled',
            ],
        )

        logger.info('Launching Rabby Wallet...')
        rabby_wallet = RabbyWalletWithPlaywright(
            config=Config(
                logger=logger,
                store_identificator='mhmoonbcjahgigdhnmnlnppcgnlkmjim',
            ),
            browser_context=context,
        )
        openion = Openion(
            url='https://openion.com/i/2mMykkBndKR',
            browser_context=context,
            logger=logger,
        )

        await rabby_wallet.import_by_private_key(PRIVATE_KEY) # type: ignore

        await openion.get_rabby_wallet()
        await openion.connect_rabby(rabby_wallet.store_identificator)
        print(await openion.get_ref_code())
        await context.close()


asyncio.run(import_rabby_wallet())
