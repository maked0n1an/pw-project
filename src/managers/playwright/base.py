import asyncio
import random
from logging import Logger
from typing import List, Literal, Optional

from patchright.async_api import (
    BrowserContext,
    ElementHandle,
    Page,
    expect
)

from .types import (
    ClickByCordsProps,
    ClickProps,
    GetElementAttributeProps,
    GetElementProps,
    TypeInInputOptions
)
from src.utils import sleep, sleep_by_range


class PlaywrightManager:
    def __init__(
        self,
        browser_context: BrowserContext,
        logger: Logger,
    ) -> None:
        self.browser_context = browser_context
        self.logger = logger

    async def get_all_pages(self) -> List[Page]:
        try:
            self.logger.info('Getting all pages...')

            pages = self.browser_context.pages

            if not pages:
                err_msg = 'No pages found'
                self.logger.error(err_msg)
                raise Exception(err_msg)

            return pages
        except Exception as e:
            self.logger.error(
                f'Error while retrieving pages from browser: {e}')
            return []
    
    async def open_extension_popup(
        self,
        url: str,
        timeout: int = 15
    ) -> Page:
        extension_page = None
        
        for page in self.browser_context.pages:
            if url == page.url:
                extension_page = page
                break
            
        if not extension_page:
            try:
                extension_page = await self.browser_context.wait_for_event(
                    'page',
                    timeout=timeout * 1000,
                )
            except TimeoutError:
                err_msg = f'Error: extension page hasn\'t opened in {timeout} seconds'
                self.logger.error(err_msg)
                raise Exception(err_msg)

        await extension_page.bring_to_front()
        return extension_page

    async def open_page(
        self,
        url: Optional[str] = None,
        timeout: int = 10,
    ) -> Page:
        try:
            self.logger.info(f'Opening new browser page with url: {url}...')

            page = await self.browser_context.new_page()

            if url:
                await page.goto(url, timeout=timeout * 1000)

            return page
        except Exception as e:
            err_msg = f'Error while opening new browser page with url: {url}. Error: {e}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def click(
        self,
        props: ClickProps,
    ) -> None:
        page = props['page']
        locator = props['locator']
        max_attempts = props.get('max_attempts', 5)
        wait_before_action = props.get('wait_before_action', 0)
        delay_between_attempts = props.get('delay_between_attempts', 1)
        delay_to_wait_element = props.get('delay_to_wait_element', 10)
        is_required = props.get('is_required', True)
        show_attempt_log = props.get('show_attempt_log', False)
        click_count = props.get('click_count', 1)

        self.logger.info(f'Clicking on an element with locator: {locator}')
        await sleep(wait_before_action, self.logger)

        is_success_click = False
        attempts = 0

        while attempts < max_attempts: # type: ignore
            try:
                timeout = delay_to_wait_element * 1000 # type: ignore
                await page.locator(locator).click(
                    timeout=timeout,
                    click_count=click_count
                )
                is_success_click = True
                break
            except Exception as e:
                if show_attempt_log:
                    self.logger.warning(
                        f'Attempt {attempts + 1} of {max_attempts}')
            finally:
                attempts += 1
                await sleep(delay_between_attempts, self.logger) # type: ignore

        if not is_success_click and is_required:
            err_msg = f'No element was clicked with locator: {locator}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def click_by_cords(
        self,
        props: ClickByCordsProps,
    ) -> None:
        page = props['page']
        locator = props['locator']
        max_attempts = props.get('max_attempts', 5)
        delay_between_attempts = props.get('delay_between_attempts', 1)
        is_required = props.get('is_required', True)
        delay_to_wait_element = props.get('delay_to_wait_element', 30)
        show_attempt_log = props.get('show_attempt_log', False)
        click_count = props.get('click_count', 1)
        offset_x = props.get('offset_x', 0)
        offset_y = props.get('offset_y', 0)

        self.logger.info(f'Clicking on an element with locator: {locator}')

        is_success_click = False
        attempts = 0

        while attempts < max_attempts: # type: ignore
            try:
                timeout = delay_to_wait_element * 1000 # type: ignore
                element_locator = page.locator(locator)
                await expect(element_locator).to_be_visible(timeout=timeout)
                box = (
                    await element_locator.bounding_box()  # type: ignore
                    or {'x': 0, 'y': 0, 'width': 0, 'height': 0}
                )

                center_x = box['x'] + box['width'] / (offset_x or 2)
                center_y = box['y'] + box['height'] / (offset_y or 2)

                if box:
                    await page.mouse.move(center_x, center_y)

                await sleep_by_range((0.1, 0.5))

                await page.hover(locator, timeout=timeout)
                await page.mouse.click(
                    center_x,
                    center_y,
                    click_count=click_count,
                    delay=300
                )

                is_success_click = True
                break
            except Exception as e:
                if show_attempt_log:
                    self.logger.warning(
                        f'Attempt {attempts + 1} of {max_attempts}')
            finally:
                attempts += 1
                await sleep(delay_between_attempts, self.logger)

        if not is_success_click and is_required:
            err_msg = f'No element was clicked with locator: {locator}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def get_element(
        self,
        props: GetElementProps,
    ) -> Optional[ElementHandle]:
        page = props['page']
        locator = props['locator']
        max_attempts = props.get('max_attempts', 3)
        delay_between_attempts = props.get(
            'delay_between_attempts', 0.3)
        is_required = props.get('is_required', True)
        delay_to_wait_element = props.get(
            'delay_to_wait_element', 3)
        show_attempt_log = props.get(
            'show_attempt_log', False)

        self.logger.info(f'Searching element with locator: {locator}')

        attempts = 0
        element: Optional[ElementHandle] = None

        while attempts < max_attempts and element is None:
            try:
                if (
                    element := await page.wait_for_selector(
                        locator,
                        timeout=delay_to_wait_element * 1000
                    )
                ):
                    return element

                if show_attempt_log:
                    self.logger.warning(
                        f'Attempt {attempts + 1} of {max_attempts}')
            except Exception as err:
                if show_attempt_log:
                    self.logger.warning(
                        f'Attempt {attempts + 1} of {max_attempts}')
            finally:
                attempts += 1
                await sleep(delay_between_attempts)

        if element is None and is_required:
            err_message = f'No element was found by locator: {locator}'
            self.logger.error(err_message)
            raise Exception(err_message)

        return element

    async def get_element_with_retry(
        self,
        page: Page,
        locator: str,
        max_attempts: int = 3,
        delay: tuple = (0.3, 0.5)  # Using a tuple to represent the range
    ) -> ElementHandle:
        self.logger.info(f'Searching element with locator: {locator}')

        attempts = 0
        element: Optional[ElementHandle] = None

        while attempts < max_attempts and element is None:
            try:
                if (element := await page.wait_for_selector(
                    locator,
                    timeout=random.randint(1300, 2100)
                )):
                    return element

                self.logger.warning(
                    f'Attempt {attempts + 1} of {max_attempts}')
            except Exception as err:
                self.logger.warning(
                    f'Attempt {attempts + 1} of {max_attempts}')
            finally:
                attempts += 1
                await sleep(random.uniform(*delay))

        if element is None:
            err_message = f'No element was found by locator: {locator}'
            self.logger.error(err_message)
            raise Exception(err_message)

        return element

    async def get_element_attribute(
        self,
        props: GetElementAttributeProps,
    ) -> Optional[str]:
        page = props['page']
        locator = props['locator']
        attribute = props['attribute']

        try:
            self.logger.info(
                f'Searching {attribute} attribute of element with locator: {locator}')
            return await page.get_attribute(selector=locator, name=attribute)
        except Exception as e:
            err_msg = f'Error while getting element attribute: {e}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def close_page(
        self,
        page: Page,
        delay: Optional[float] = 0.25,
    ) -> None:
        if delay:
            await sleep(delay, self.logger)
        
        try:
            self.logger.info('Closing page...')
            await page.close()
        except Exception as e:
            err_msg = f'Error while closing page: {e}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def close_unused_pages(
        self,
        pages: List[Page],
    ) -> None:
        try:
            self.logger.info('Closing unused pages...')
            for page in pages:
                await self.close_page(page)
        except Exception as e:
            err_msg = f'Error while closing unused pages: {e}'
            self.logger.error(err_msg)
            raise Exception(err_msg)

    async def find_page_by_value(
        self,
        value: str,
        type: Literal['url', 'title']
    ) -> Page:
        try:
            self.logger.info(f'Looking for page by value: {value}')

            pages = await self.get_all_pages()
            page_promises = [
                self._get_page_value(page, value, type) for page in pages
            ]
            matched_pages = await asyncio.gather(*page_promises)
            filtered_pages = [page for page in matched_pages if page]

            if not filtered_pages:
                err_message = '0 pages were found'
                self.logger.error(err_message)
                raise Exception(err_message)

            if len(filtered_pages) > 1:
                self.logger.info('Closing extra pages...')
                await self.close_unused_pages(filtered_pages)

            return filtered_pages[0]
        except Exception as err:
            err_message = f'Searching page failed: {err}'
            self.logger.error(err_message)
            raise Exception(err_message)

    async def clear_input(
        self,
        page: Page,
        locator: str,
    ) -> None:
        try:
            element = await self.get_element_with_retry(page, locator)
            self.logger.info(f'Clearing input with locator: {locator}')
            await element.fill('')
        except Exception as err:
            err_message = f'Error while clearing input: {err}'
            self.logger.error(err_message)
            raise Exception(err_message)

    async def type_in_input(
        self,
        props: TypeInInputOptions,
    ) -> None:
        page = props['page']
        locator = props['locator']
        text = props['text']
        is_required = props.get('is_required', True)
        wait_time = props.get('wait_time', 3)

        try:
            element = await self.get_element_with_retry(page, locator)
            self.logger.info(f'Typing in input with locator: {locator}')
            await element.fill(text, timeout=wait_time * 1000)
        except Exception as err:
            if is_required:
                err_message = f'Error while typing in input: {err}'
                self.logger.error(err_message)
                raise Exception(err_message)

    async def _get_page_value(
        self,
        page: Page,
        value: str,
        type: Literal['url', 'title']
    ) -> Optional[Page]:
        if type == 'title':
            result = await page.title()
        elif type == 'url':
            result = page.url

        return page if value in result else None
