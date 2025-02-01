import logging

from patchright.async_api import BrowserContext


from .constants import OpenionXPath
from src.managers.playwright.base import PlaywrightManager


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
        openion = await self.pw_manager.open_page(url=self.url)
        
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
        rabby_popup = f"chrome-extension://{chrome_store_id}/notification.html"
        
        extension_page = await self.pw_manager.open_extension_popup(url=rabby_popup)
        await self.pw_manager.click({
            'page': extension_page,
            'locator': OpenionXPath.RABBY_APPROVAL,
            'delay_to_wait_element': 1,
        })
        await self.pw_manager.click({
            'page': extension_page,
            'locator': OpenionXPath.SIGN,
            'delay_to_wait_element': 1,
        })
        await self.pw_manager.close_page(extension_page)
        
        sign_popup = await self.pw_manager.open_extension_popup(
            url=rabby_popup + '#/approval',
            timeout=100
        )
        await self.pw_manager.click({
            'page': sign_popup,
            'locator': OpenionXPath.CONFIRM_SIGN,
            'click_count': 2,
        })
        
    async def get_ref_code(self) -> str:
        account_page = await self.pw_manager.open_page(
            'https://openion.com/account/active'
        )
        ref_code = await account_page.locator(OpenionXPath.REF_CODE).inner_html()
        return ref_code
