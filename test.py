import asyncio
from fake_useragent import UserAgent

from patchright.sync_api import sync_playwright, expect
from patchright.async_api import async_playwright, expect
# from playwright.sync_api import sync_playwright
# from playwright.async_api import async_playwright, expect


def sync_work():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=False)
        page = browser.new_page()
        
        page.goto('https://whatmyuseragent.com/')
        page.screenshot(path='./demo.png')
        browser.close()
        
async def async_work():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=False)
        page = await browser.new_page()
        
        await page.goto('https://whatmyuseragent.com/')
        await page.screenshot(path='./demo.png')
        
        await browser.close()
        
async def grab_user_agent():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            channel='chrome',
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        page = await browser.new_page()
        await page.goto('https://whatmyuseragent.com/')
        user_agent = page.locator('#ua')
        user_agent_text = await user_agent.inner_html()
        # await expect(user_agent).to_be_visible()
        # await expect(user_agent).to_have_text(user_agent_text)
        print(user_agent_text)
        await browser.close()
        
async def grab_all_nav_links():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(channel='chrome', headless=False)
        
        page = await browser.new_page()
        await page.goto('https://whatmyuseragent.com/')
        
        nav_links = await page.locator('#navbarNavAltMarkup > div > a').all()
        for link in nav_links:
            text = await link.inner_text()
            url = await link.get_attribute('href')
            print(f'{text} - {url}')
        await browser.close()
        

async def antidetect_work():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            channel='chrome',
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        user_agent = UserAgent().random
        print('UA полученный: ', user_agent)
        
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        await page.goto('https://whatmyuseragent.com/')
        
        el = page.locator('#ua')
        await expect(el).to_be_visible()
        ua = await el.inner_text()
        print('UA на странице: ', ua)
        
        await browser.close()
        
async def check_is_automated():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            channel='chrome',
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        
        page = await browser.new_page()
        await page.goto('https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html')
        await page.wait_for_timeout(10000)
        await browser.close()


asyncio.run(antidetect_work())
