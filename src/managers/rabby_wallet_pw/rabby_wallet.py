import asyncio
from faker import Faker
from patchright.async_api import (
    BrowserContext,
    expect,
)

from .constants import RABBY_WALLET_URL, RabbyXPath
from .types import Config
from ..playwright import PlaywrightManager

class RabbyWalletWithPlaywright:
    def __init__(
        self,
        config: Config,
        browser_context: BrowserContext,
    ) -> None:
        self.logger = config.get('logger')
        self.store_identificator = config.get('store_identificator', '')
        self.pw_manager = PlaywrightManager(
            browser_context=browser_context,
            logger=self.logger,
        )
        
    def _exist_check(
        self,
        value: str | object | None,
        msg: str = ''
    ) -> None:
        if value:
            return
        
        err_msg = f'Missing required value: {msg}'
        self.logger.error(err_msg)
        raise Exception(err_msg)
        
    async def import_by_private_key(self, private_key: str):
        self.logger.info('Importing Rabby Wallet by private key...')
        
        evm_password = Faker().password(
            length=16,
            special_chars=True,
            digits=True,
            upper_case=True,
        )
        
        for page in self.pw_manager.browser_context.pages:
            if page.url == 'about:blank':
                _ = asyncio.create_task(
                    self.pw_manager.close_page(page, delay=2),
                )
        
        page = await self.pw_manager.open_page(url=RABBY_WALLET_URL)
        await expect(page).to_have_url(RABBY_WALLET_URL)
    
        await self.pw_manager.click({
            'page': page,
            'locator': RabbyXPath.I_ALREADY_HAVE_AN_ACCOUNT,
        })
        await self.pw_manager.click({
            'page': page,
            'locator': RabbyXPath.PRIVATE_KEY,
        })
        await self.pw_manager.type_in_input({
            'page': page,
            'locator': RabbyXPath.PRIVATE_KEY_INPUT,
            'text': private_key,
        })
        await self.pw_manager.click({
            'page': page,
            'locator': RabbyXPath.CONFIRM,
        })
        await self.pw_manager.type_in_input({
            'page': page,
            'locator': RabbyXPath.ENTER_PASSWORD,
            'text': evm_password,
        })
        await self.pw_manager.type_in_input({
            'page': page,
            'locator': RabbyXPath.CONFIRM_PASSWORD,
            'text': evm_password,
        })
        await self.pw_manager.click({
            'page': page,
            'locator': RabbyXPath.CONFIRM_IMPORT,
        })
        await self.pw_manager.click({
            'page': page,
            'locator': RabbyXPath.DONE_BUTTON,
        })
        await self.pw_manager.close_page(page)