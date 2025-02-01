import logging

from patchright.async_api import BrowserContext, expect


from .constants import OpenionXPath
from src.managers.playwright.base import PlaywrightManager
from src.managers.rabby_wallet_pw.constants import RABBY_WALLET_URL


class Openion:
    def __init__(
        self,
        url: str,
        browser_context: BrowserContext,
        logger: logging.Logger,
    ) -> None:
        self.url = url
        self.logger = logger
        self.pw_manager = PlaywrightManager(
            browser_context=browser_context,
            logger=self.logger,
        )
    
    async def get_rabby_wallet(self) -> None:
        openion = await self.pw_manager.browser_context.new_page()
        await openion.goto(self.url)
        
        await self.pw_manager.click({
            'page': openion,
            'locator': OpenionXPath.EXPLORE_MARKETS,
            'delay_to_wait_element': 1,
        })
        await self.pw_manager.click({
            'page': openion,
            'locator': OpenionXPath.LOG_IN,
            'delay_to_wait_element': 1,
        })
        await openion.get_by_text('Rabby Wallet', exact=True).click()
        
    async def connect_rabby(
        self,
        chrome_store_id: str,
    ) -> None:
        rabby_popup = f"chrome-extension://{chrome_store_id}/notification.html#/approval"
        
        extension_page = await self.pw_manager.open_extension_popup(url=rabby_popup)
        await self.pw_manager.click({
            'page': extension_page,
            'locator': '//*[@id="root"]/div/div/div/div/div[3]/div/div/div/span[2]',
            'delay_to_wait_element': 1,
        })
        await self.pw_manager.click({
            'page': extension_page,
            'locator': '//*[@id="root"]/div/div/div/div/div[3]/div/div/button[1]',
            'delay_to_wait_element': 1,
        })
        await self.pw_manager.close_page(extension_page)
        
        sign_popup = await self.pw_manager.open_extension_popup(
            url=rabby_popup,
            timeout=100
        )
        await self.pw_manager.click({
            'page': sign_popup,
            'locator': '//*[@id="root"]/div/footer/div/section/div[2]/div/button',
            'click_count': 2,
        })
